# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_mactable.c

## Purpose
`sparx5_mactable.c` owns the Sparx5 hardware MAC address table access path and the driver's software shadow of bridge-learned FDB entries. It provides CPU commands for learning, lookup, scanning, and forgetting MAC entries, synchronizes multicast addresses to the CPU PGID, periodically pulls dynamic hardware-learned entries into Linux bridge switchdev state, ages deleted entries out of the software list, and initializes/deinitializes the MAC table workqueue.

The file bridges three domains: LRN hardware registers, in-kernel switchdev FDB notifications, and driver-local state in `struct sparx5::{mact_entries,mact_lock,mact_work,mact_queue,bridge_mask}`.

## Important APIs, Types, And Functions
`struct sparx5_mact_entry` is the software shadow entry. It stores `mac`, `vid`, `port`, list membership, and flags: `MAC_ENT_ALIVE` for entries observed during the current scan, `MAC_ENT_MOVED` for entries whose hardware port changed, and `MAC_ENT_LOCK` for permanent/static entries that should not be aged by the pull worker.

Hardware command constants encode `LRN_COMMON_ACCESS_CTRL` CPU commands: learn, unlearn, lookup, read, write, scan, find-smallest, and clear-all. Address type constants distinguish port/UPSID entries from CPU/internal, GLAG, and multicast-index entries. `TABLE_UPDATE_SLEEP_US` and `TABLE_UPDATE_TIMEOUT_US` bound `readx_poll_timeout()` waits for `MAC_TABLE_ACCESS_SHOT` to clear.

The exported API includes:

- `sparx5_mact_learn()` programs a MAC/VLAN entry to either a physical port/UPSID or a multicast PGID index, marks it valid and locked, issues `MAC_CMD_LEARN`, and waits for completion.
- `sparx5_mact_find()` selects a MAC/VLAN key, issues `MAC_CMD_LOOKUP`, and returns `cfg2` only if the valid bit is set.
- `sparx5_mact_forget()` issues `MAC_CMD_UNLEARN` for a MAC/VLAN key.
- `sparx5_mact_getnext()` uses `MAC_CMD_FIND_SMALLEST` with scan-next settings to iterate the table after a supplied key.
- `sparx5_add_mact_entry()` handles bridge/static FDB additions: avoid duplicate hardware/software entries, add a shadow entry when needed, program hardware, mark the entry locked, and notify bridge offload state.
- `sparx5_del_mact_entry()` removes all matching shadow entries, optionally across all VIDs when `vid == 0`, and unlearns matching hardware entries.
- `sparx5_mc_sync()` and `sparx5_mc_unsync()` sync netdev multicast filters to the CPU PGID using the port PVID.
- `sparx5_set_ageing()` converts bridge ageing time from milliseconds to LRN autoage register units.
- `sparx5_mact_init()` flushes the hardware table, sets default ageing, learns the broadcast address to CPU for `NULL_VID`, initializes MDB/MACT locks and lists, creates a single-thread workqueue, and starts delayed polling.
- `sparx5_mact_deinit()` cancels delayed work, destroys the queue, and destroys `mact_lock`.

Internal helpers include `sparx5_mact_select()` for encoding MAC+VID into access registers, `sparx5_mact_get()` for decoding current access registers, `alloc_mact_entry()` and `find_mact_entry()` for software-list management, `sparx5_fdb_call_notifiers()` for switchdev notification construction, `sparx5_mact_handle_entry()` for one scanned hardware entry, and `sparx5_mact_pull_work()` for periodic full-table synchronization.

## Control Flow
Direct hardware access follows a consistent sequence: take `sparx5->lock`, call `sparx5_mact_select()` if the command is keyed by MAC/VLAN, write command-specific configuration registers, set `MAC_TABLE_ACCESS_SHOT`, poll for completion, read back state if required, then release the lock. This serializes LRN access registers across learn, lookup, scan, and unlearn operations.

Static bridge additions enter through `sparx5_add_mact_entry()`. The function first checks the hardware table. If the entry already exists, it returns success. Otherwise it checks the software list to avoid re-adding a hardware-learned entry that might already have been shadowed. New software entries are allocated with device-managed memory, appended under `mact_lock`, then hardware is programmed through `sparx5_mact_learn()`. First-time entries are marked `MAC_ENT_LOCK` and advertised to the bridge with `SWITCHDEV_FDB_ADD_TO_BRIDGE` and `offloaded = true`.

Periodic learning synchronization runs in `sparx5_mact_pull_work()`. The worker clears all non-lock flags, scans the hardware MAC table from MAC zero/VID zero with repeated `FIND_SMALLEST` commands, and passes each valid result to `sparx5_mact_handle_entry()`. That handler only accepts physical port entries, rejects invalid front-port indexes, and only reports ports currently in `bridge_mask`. Existing entries are marked alive; moved entries update `port`, set `MAC_ENT_MOVED`, and notify the bridge as an add on the new netdev. New entries are appended and notified as offloaded adds. After the scan ends, the worker removes software entries that are neither alive nor locked, sends `SWITCHDEV_FDB_DEL_TO_BRIDGE`, frees them, and requeues itself after `SPX5_MACT_PULL_DELAY`.

Deletion through `sparx5_del_mact_entry()` is software-list driven. For every matching entry it unlearns the hardware key, removes the list item, and frees the device-managed allocation.

## State And Persistence Behavior
Hardware state persists in the switch MAC table until learned, unlearned, auto-aged, or flushed. Driver initialization clears the whole table and seeds a CPU broadcast entry. The software shadow list is volatile kernel memory tied to the device lifetime and is rebuilt as dynamic hardware entries are scanned. Static or bridge-managed entries are represented by `MAC_ENT_LOCK`, so the pull worker does not age them out when not seen in hardware.

The MAC access register block is protected by `sparx5->lock`. The software FDB list is protected by `sparx5->mact_lock`. The two locks are used independently in most paths, but `sparx5_del_mact_entry()` holds `mact_lock` while calling `sparx5_mact_forget()`, which then takes `sparx5->lock`; `sparx5_mact_pull_work()` takes and releases `sparx5->lock` around hardware scan operations, then separately takes `mact_lock` while editing flags and lists.

Memory for `sparx5_mact_entry` is allocated with `devm_kzalloc()` and freed explicitly with `devm_kfree()` when entries disappear. The workqueue is a single-thread queue, limiting concurrent pull workers. No persistent storage is used outside switch registers.

## Dependencies And Integration Points
The file depends on `sparx5_main.h` for `struct sparx5`, constants such as `NULL_VID` and `SPX5_MACT_PULL_DELAY`, register helpers, PGID helpers, and bridge masks. It depends on generated register definitions from `sparx5_main_regs.h`, especially `LRN_*` fields. It uses Linux switchdev notifier APIs to tell the bridge about offloaded FDB adds/deletes, Linux bridge default ageing time, netdev private data for `sparx5_port`, and `readx_poll_timeout()` for register command completion.

The main probe path in `sparx5_main.c` calls `sparx5_mact_init()` after VCAP initialization and before stats/frame I/O/PTP/netdev registration. Remove and probe error unwind call `sparx5_mact_deinit()`. Switchdev/bridge code calls `sparx5_add_mact_entry()`, `sparx5_del_mact_entry()`, multicast sync helpers, and ageing configuration.

## Risks
`sparx5_mact_handle_entry()` releases `mact_lock` before using `mact_entry->flags` in the `found && !(mact_entry->flags & MAC_ENT_MOVED)` check; the worker is single-threaded, but other FDB add/delete paths can mutate the list under `mact_lock`, so this deserves scrutiny for lifetime and flag-race safety. `sparx5_del_mact_entry()` holds `mact_lock` while issuing hardware unlearn commands that can sleep/poll for up to 100 ms, extending list lock hold time. `sparx5_mact_init()` calls `sparx5_mact_learn()` before `mact_lock` and `mact_entries` initialization, which is safe for direct hardware learning but means future changes must not make learn depend on software-list state.

Other risks include silent timeout handling in periodic scans, no explicit deinit freeing of leftover `mact_entries` before destroying the lock, reliance on correct PGID/type mapping for multicast entries, and table iteration semantics depending on the hardware `FIND_SMALLEST` command making forward progress from the previous MAC/VID key.

## Test Signals
Useful signals include bridge FDB add/delete notifications with `offloaded` state, `bridge fdb show` after hardware learning and ageing, multicast address sync/unsync on a port PVID, MAC moves between bridged ports, removal of dynamically learned entries after hardware ageing, and timeout/error logs from MAC flush or access polling. Lockdep/KASAN testing should focus on concurrent bridge FDB operations while `sparx5_mact_pull_work()` scans and prunes entries. Hardware tests should cover physical-port entries, CPU PGID multicast entries, VLAN zero and nonzero VIDs, and failure injection for workqueue allocation.
