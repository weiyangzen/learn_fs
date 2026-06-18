# Research: subset-b-004574

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_mactable.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_mactable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main.c

## Purpose
`sparx5_main.c` is the platform-driver entry point and top-level hardware bring-up file for the Microchip Sparx5 switch driver, with optional LAN969x match data support. It maps register targets, interprets device-tree port configuration, resets and initializes the switch core, configures the core clock and shared forwarding resources, creates per-port netdev/phylink state, starts major subsystems, and performs ordered teardown.

It also supplies the Sparx5-specific static target map, register table pointers, hardware constants, operation callbacks, Open Firmware match table, and module registration.

## Important APIs, Types, And Functions
The local `struct initial_port_config` is a staging record populated from device tree before netdev creation; it keeps `portno`, `device_node`, `sparx5_port_config`, and optional SerDes PHY. `struct sparx5_ram_config` pairs memory-init registers with the bit values that need to be asserted and later observed as cleared.

`sparx5_main_iomap[]` maps every Sparx5 register target to an offset within one of three platform memory resources. `sparx5_create_targets()` consumes this table and fills `sparx5->regs[target]` base pointers so `spx5_rd()`, `spx5_wr()`, and `spx5_rmw()` can address generated register macros uniformly.

Target/feature helpers:

- `is_sparx5()` returns true for native Sparx5 target chip IDs and false for LAN969x variants.
- `sparx5_init_features()` enables PSFP and PTP feature bits on supported Sparx5 and LAN969x IDs.
- `sparx5_has_feature()` tests a feature bit in `sparx5->features`.

Bring-up helpers:

- `sparx5_create_port()` allocates a netdev, initializes `struct sparx5_port` defaults, calls `sparx5_port_init()`, sets VLAN defaults, configures phylink capabilities based on port bandwidth and RGMII support, creates phylink, and attaches the OF node.
- `sparx5_init_ram()` asserts reset/init bits for key memories and counters, then polls up to ten 1-2 ms intervals for the bits to clear.
- `sparx5_init_switchcore()` force-initializes EACL policer state, conditionally initializes RAM if the core is not enabled, resets counters, and enables the switch core/queue system.
- `sparx5_init_coreclock()` chooses a supported core clock for the target, configures LCPLL for native Sparx5, updates `sparx5->coreclock`, and writes clock-period-dependent values into HSCH, policer, LRN autoage, SIO clock, TAS, and policer update registers.
- `sparx5_qlim_set()` and `qlim_wm()` configure QRES limits and XQS shared queue watermarks from target buffer size.
- `sparx5_frame_io_init()` prefers FDMA when an FDMA IRQ is usable and falls back to register-based extraction/injection through the XTR IRQ and manual injection mode.
- `sparx5_frame_io_deinit()` disables selected frame I/O IRQs and deinitializes FDMA when active.
- `sparx5_board_init()` optionally remaps SGPIO signal-detect lines to ports based on `microchip,sd-sgpio` device-tree properties.
- `sparx5_forwarding_init()` programs own UPSIDs, enables internal CPU ports, initializes forwarding and flood PGIDs, enables CPU copy for CPU/broadcast PGIDs, forces FCS update for injected frames, and applies queue limits.

Driver entry points:

- `mchp_sparx5_probe()` is the full probe sequence.
- `mchp_sparx5_remove()` tears subsystems down in reverse operational order.
- `mchp_sparx5_match[]` matches `"microchip,sparx5-switch"` to `sparx5_desc` and LAN969x-compatible strings to `lan969x_desc` when enabled.

Static exported data includes `sparx5_regs`, `sparx5_consts`, `sparx5_ops`, and `sparx5_desc`. `sparx5_ops` binds port classification, muxing, PTP IRQ handling, calendar calculation, FDMA init/deinit/poll/transmit, and scheduler helper callbacks.

## Control Flow
Probe starts by validating a device tree or platform data source, allocating `struct sparx5` with devm memory, saving platform driver data, initializing `tx_lock`, loading match data, setting the global `regs` pointer, and resetting the optional shared switch reset controller.

The probe then creates `debugfs_root`, locates the `ethernet-ports` child node, counts ports, and builds an array of `initial_port_config` records. Each available port node must supply `reg`, `phy-mode`, and `microchip,bandwidth`. Optional `microchip,sd-sgpio` enables board-level signal-detect remapping. Non-RGMII ports must provide a SerDes PHY. Defaults such as DAC media, SerDes reset, port mode, and power-down are staged before actual port creation.

After parsing ports, `sparx5_create_targets()` maps platform memory resources and fills target bases. Probe establishes a base MAC from OF or a random fallback, reads IRQs, reads chip ID, derives `target_ct`, initializes feature bits, initializes switch core RAM, and configures the core clock. It then creates each staged port, initializes PGIDs and VLANs, applies board and forwarding setup, initializes calendar/QoS/VCAP/MAC table/stats/frame I/O/PTP subsystems, registers netdevs, and finally registers notifier blocks.

Error handling uses goto labels to unwind only the subsystems that have been initialized so far: unregister netdevs, PTP, frame I/O, stats, MAC table, VCAP, netdev destruction, config allocation, and the OF ports node. Successful probe jumps to `cleanup_config`, freeing the temporary config array and dropping the OF node reference while leaving persistent driver state active.

Remove removes debugfs, unregisters notifiers and netdevs, then deinitializes PTP, frame I/O, stats, MAC table, VCAP, and netdevs.

## State And Persistence Behavior
The central persistent runtime object is `struct sparx5`, owned by the platform device and allocated with devm memory. It stores register mappings, chip ID, target type, feature bits, ports, locks, per-subsystem workqueues, notifier blocks, frame I/O state, PTP state, VCAP state, PGID map, mirror entries, and match data.

Hardware state is initialized in an ordered sequence: switch memories and counters, core/clock, port hardware, PGIDs/VLANs/forwarding, scheduling/QoS/VCAP/MACT/statistics, frame I/O, and PTP. Many values survive as switch register state until reset or driver removal, while software state is volatile and recreated on probe.

Temporary device-tree parse state is allocated with `kzalloc_objs()` and freed before returning from probe. Port OF node references are kept in `sparx5_port::of_node`; the loop uses `for_each_available_child_of_node()`, and explicit `of_node_put()` appears in the SerDes error path and for the parent ports node.

The file initializes `tx_lock` early. Other locks and lists are initialized by subsystem-specific init functions, for example MAC table and stats code. `debugfs_root` is removed in `remove()`, but if probe fails after creating it and before successful bind, the failure path shown here does not explicitly remove it.

## Dependencies And Integration Points
The file depends heavily on generated register metadata from `sparx5_main_regs.h` and the register access helpers declared in `sparx5_main.h`. It includes subsystem headers for port, QoS, VCAP, and LAN969x match data. It integrates with the Linux platform bus, OF device-tree parsing, reset controller framework, phylink, PHY/SerDes, IRQ registration, debugfs, switchdev, netdev registration, and kernel module infrastructure.

Subsystem integration points are explicit in probe: `sparx5_pgid_init()`, `sparx5_vlan_init()`, `sparx5_calendar_init()`, `sparx5_qos_init()`, `sparx5_vcap_init()`, `sparx5_mact_init()`, `sparx5_stats_init()`, `sparx5_frame_io_init()`, `sparx5_ptp_init()`, `sparx5_register_netdevs()`, and `sparx5_register_notifier_blocks()`. `sparx5_forwarding_init()` uses PGID and internal-port helpers and prepares CPU ports for packet I/O. `sparx5_frame_io_init()` delegates to FDMA ops supplied by match data and falls back to packet register I/O helpers.

`sparx5_desc` supplies native Sparx5 `iomap`, register tables, constants, and ops. The OF table allows the same platform driver to bind native Sparx5 and, when configured, LAN969x devices with their own match data.

## Risks
The global `const struct sparx5_regs *regs` is set from the probed device match data. If multiple variants could be probed simultaneously, generated register helpers or users of this global need review for cross-device assumptions. `sparx5_create_targets()` assumes the iomap is ordered by range so `range_id[]` is initialized as expected; malformed match data could leave range indexing fragile. `IO_RANGES` is fixed at three, while match data also provides `ioranges`, so variants with more ranges would need code changes.

Probe failure after `debugfs_create_dir()` does not visibly remove `debugfs_root` on all error paths. `sparx5_create_port()` sets `sparx5->ports[portno]` before `sparx5_port_init()` and phylink creation complete; unwind through `sparx5_destroy_netdevs()` must tolerate partially initialized ports. Device-tree parse errors for individual ports often log and `continue`, which can reduce initialized port count without failing the whole probe unless later stages depend on those configs.

Frame I/O fallback mutates IRQ fields to `-ENXIO` on failure; later deinit depends on those sentinels. Core-clock support differs by target, so tests must catch invalid clock combinations. The remove path assumes all listed subsystems were initialized on successful probe; any future optional subsystem must preserve this ordering.

## Test Signals
Probe tests should cover native Sparx5 and LAN969x match data, missing or malformed `ethernet-ports`, missing `phy-mode`/bandwidth, RGMII ports without SerDes, non-RGMII ports with missing SerDes, absent base MAC, unavailable FDMA IRQ with XTR fallback, and FDMA success. Hardware bring-up signals include memory initialization timeout logs, core-clock register programming, PGID/flood mask state, CPU port enablement, netdev registration, PTP init, notifier registration, and clean removal. Failure-injection tests should target allocation failures, phylink creation failures, IRQ request failures, VCAP/MACT/stats/PTP init failures, and confirm that each goto label unwinds only initialized resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main.h

## Purpose
`sparx5_main.h` is the central internal contract for the Sparx5 switch driver. It defines target IDs, port/VLAN/calendar/feature constants, frame DMA and PTP state, port and switch-wide runtime structures, match-data abstractions, subsystem prototypes, and inline register access helpers used across the driver.

The header is both a device model definition and a cross-file API surface. Most Sparx5 source files include it to access `struct sparx5`, `struct sparx5_port`, shared constants, hardware ops, and register read/write helpers.

## Important APIs, Types, And Functions
Target and configuration enums include `enum spx5_target_chiptype` for native Sparx5 and LAN969x part IDs, `enum sparx5_port_max_tags`, `enum sparx5_vlan_port_type`, `enum sparx5_cal_bw`, `enum sparx5_feature`, and `enum sparx5_core_clockfreq`.

Core constants define front and internal port counts (`SPX5_PORTS`, `SPX5_PORTS_ALL`), internal CPU/VD port indexes, PGID indexes, IFH length and rewrite/PDU encodings, MAC table pull delay, stats delay, priority count, buffer cell size, FDMA channel/DCB sizes, PTP PHC count, calendar dimensions, and PSFP/SDLB limits.

Important state types:

- `struct sparx5_calendar_data` stores DSM calendar calculation scratch arrays.
- `struct sparx5_rx`, `struct sparx5_tx_buf`, and `struct sparx5_tx` describe FDMA RX/TX rings, SKB/page ownership, DMA addresses, NAPI, counters, and transmit buffer state.
- `struct sparx5_port_config` stores per-port media, bandwidth, PHY mode, autoneg/pause, power, SerDes reset, and signal-detect settings.
- `struct sparx5_port` is the per-netdev private object with netdev, parent `sparx5`, OF/SerDes/phylink state, VLAN defaults, signal-detect state, injection timer, PTP TX tracking, mrouter flag, and TC template list.
- `struct sparx5_phc` and `struct sparx5_skb_cb` hold PTP clock and per-SKB timestamping metadata.
- `struct sparx5_mdb_entry`, `struct sparx5_mall_entry`, and mirror-related structs model multicast database and matchall mirror state.
- `struct sparx5_regs` points to generated register metadata arrays. `struct sparx5_consts` stores target-specific capacities and VCAP metadata. `struct sparx5_ops` stores target-specific callbacks for port classification, muxing, scheduling, PTP, calendar, and FDMA operations. `struct sparx5_main_io_resource` maps target IDs to resource offsets. `struct sparx5_match_data` bundles all per-compatible match data.
- `struct sparx5` is the top-level device state: platform device, `dev`, chip identity, feature bits, mapped target bases, ports, locks, statistics work, notifier blocks, bridge masks, VLAN masks, MAC/MDB lists, workqueues, frame I/O IRQs and FDMA state, PTP state and locks, VCAP control, PGID map, mirror entries, debugfs root, and match data.

The header declares subsystem APIs for switchdev notifiers, packet extraction/injection, FDMA, MAC table, VLAN/PGID, calendar, ethtool stats, optional DCB, netdev/IFH helpers, PTP, VCAP, pool allocation, port muxing/internal-port mapping, SDLB, policing, PSFP, QoS base-time adjustment, and mirror offload.

Inline helpers:

- `sparx5_clk_period()` maps core clock enum to picoseconds.
- `sparx5_is_baser()` identifies 5G/10G/25G BASE-R PHY interfaces.
- `spx5_offset()` computes a raw generated-register offset and warns on out-of-range target/group/register instances.
- `spx5_addr()` and `spx5_inst_addr()` compute MMIO addresses from generated register parameters.
- `spx5_rd()`, `spx5_wr()`, and `spx5_rmw()` perform normal read/write/read-modify-write operations against `sparx5->regs`.
- `spx5_inst_rd()`, `spx5_inst_wr()`, and `spx5_inst_rmw()` do the same for a supplied target base pointer.
- `spx5_inst_get()` returns a target-instance base pointer.
- `spx5_reg_get()` returns the computed MMIO address for a generated register.

## Control Flow
The header itself does not execute probe logic, but it shapes cross-module control flow. `sparx5_main.c` allocates and fills `struct sparx5`, maps target bases into `regs[]`, and invokes the subsystem init functions declared here. Packet, FDMA, PTP, VCAP, VLAN, MACT, QoS, and port modules then use the shared object and inline register helpers to operate on hardware.

Generated register macros expand into the long argument lists consumed by `spx5_rd()`, `spx5_wr()`, `spx5_rmw()`, and address helpers. This design lets call sites write compact register names such as `spx5_rd(sparx5, GCB_CHIP_ID)` while the inline functions still receive target ID, instance counts, group offsets, and register offsets.

The `sparx5_ops` callback table decouples common code from native Sparx5 versus LAN969x differences. Main probe loads `sparx5->data` from OF match data and downstream code calls through `data->ops` for port type checks, muxing, FDMA behavior, PTP IRQ handling, and calendar calculations.

## State And Persistence Behavior
All structures in this header represent volatile kernel state for a bound platform device; persistent hardware state lives in registers and switch memories addressed through `regs[]`. `struct sparx5` aggregates both long-lived resources and subsystem-owned transient state. Workqueues and locks inside it serialize asynchronous stats and MAC-table work. Bitmaps track bridge membership, forwarding, learning, and VLAN membership across `SPX5_PORTS`.

`struct sparx5_port` lives as netdev private data and points back to the parent `sparx5`. FDMA RX/TX state tracks DMA mappings and SKB/page ownership that must be released by FDMA teardown code. PTP fields include spinlocks and mutexes because timestamp ID allocation, PHC clock access, and interface state cross interrupt and process contexts. The PGID map is a fixed-size byte array used by multicast/flood resource allocation.

Register helpers are stateless, but they assume `sparx5->regs` entries have been populated before use and that the generated register metadata matches the active target. `WARN_ON()` checks catch invalid instance indexes in debug/test builds but do not prevent address calculation after warning.

## Dependencies And Integration Points
The header includes Linux PHY, phylink, netdevice, VLAN, bitmap, timestamping, PTP, hrtimer, debugfs, flow offload, and FDMA APIs, plus generated Sparx5 register definitions. It is included by most driver modules and is the dependency that ties subsystem prototypes together.

Integration with Linux networking is visible through `net_device`, NAPI, switchdev notifiers, ethtool ops, DCB ops, phylink MAC/PCS ops, flow offload mirror/matchall state, and bridge/VLAN state. Hardware integration is through register target IDs, target constants, FDMA channels, PTP PHC metadata, VCAP metadata, PSFP structures, policing structures, and SDLB scheduler parameters.

Because it declares many subsystem functions, changes to this header can affect compile dependencies across the whole driver. The generated register-call ABI also means edits to helper signatures must match generated macros in `sparx5_main_regs.h`.

## Risks
`struct sparx5` is large and shared widely, so field lifetime and locking rules are implicit. Misusing `sparx5->lock` versus subsystem locks can cause races around hardware access or software lists. The register helpers use long positional parameter lists; correctness depends on generated macros passing the right values in the right order. `WARN_ON()` detects but does not sanitize out-of-range indexes, so invalid input can still produce invalid MMIO addresses.

Several constants are target-specific but named globally, such as `SPX5_PORTS`, `SPX5_BUFFER_MEMORY`, and PGID table sizing; LAN969x support relies on `sparx5_consts` for runtime capacities in many places, but compile-time arrays and bitmaps remain sized for Sparx5 limits. The global `extern const struct phylink_*` and DCB/ethtool declarations require matching definitions in other modules. Optional DCB is compiled as a no-op inline when disabled, so callers must not depend on side effects in that configuration.

## Test Signals
Build coverage should include native Sparx5, LAN969x-enabled builds, and builds with and without `CONFIG_SPARX5_DCB`. Runtime tests should validate register helper addressing with representative target/group/register instances, port bitmaps at highest valid port indexes, FDMA RX/TX setup and teardown, PTP timestamp request/release paths, MAC/MDB list operations, PGID allocation near table limits, PSFP/SDLB resource boundaries, and phylink mode negotiation across SGMII/QSGMII/BASE-X/BASE-R/RGMII interfaces. Static analysis should focus on lock ordering, MMIO helper argument correctness, and array bounds in `struct sparx5` bitmaps and fixed-size tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main.h -->
