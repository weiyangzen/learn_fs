# subset-b-004664 research

Grouped research report for TI ICSSM PRU Ethernet, K3 CPPI descriptor pool, and Keystone NetCP files. Each section is source-tree aligned and bounded for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth.c

## Purpose
This is the platform and net_device implementation for the TI PRUSS ICSSM Ethernet driver. It supports single/dual EMAC operation and runtime switch-mode offload when the two PRU Ethernet ports are enslaved to the same Linux bridge. It programs PRUSS DRAM/shared RAM/OCMC memory layouts, configures MII_RT, binds PHYs, boots PRU remoteproc firmware, handles NAPI RX, queues TX into firmware-owned rings, and registers netdevice and switchdev notifiers.

## Important APIs, types, and functions
- `icssm_prueth_probe()` discovers DT `ethernet-ports`, obtains PRU remoteprocs, PRUSS memory regions, shared SRAM/OCMC pool, MII_RT regmap, IEP, creates netdevices, registers them, and registers bridge/switchdev notifiers.
- `icssm_prueth_netdev_init()` allocates each `net_device`, initializes `struct prueth_emac`, maps port IDs to PRU/DRAM/TX/RX queues, obtains IRQ and PHY, installs `emac_netdev_ops`, NAPI, and a TX retry hrtimer.
- `icssm_emac_ndo_open()` and `icssm_emac_ndo_stop()` are the main lifecycle hooks. Open initializes shared memory on first port, configures EMAC or switch memory, initializes PTP/IEP once, boots firmware, requests IRQ, enables NAPI/PHY/port, and marks `emac_configured`. Stop clears the bit, disables port/PHY/NAPI/timer, shuts down firmware if no remaining port needs it, frees IRQ/FDB state, and exits IEP when the last port stops.
- `icssm_prueth_tx_enqueue()`, `icssm_emac_ndo_start_xmit()`, `icssm_emac_rx_packets()`, and `icssm_emac_rx_packet()` implement the shared-memory datapath.
- `icssm_prueth_change_mode()`, `icssm_prueth_ndev_port_link()`, `icssm_prueth_ndev_port_unlink()`, and `icssm_prueth_port_offload_fwd_mark_update()` handle bridge membership and firmware mode changes.
- `icssm_emac_ndo_set_rx_mode()` programs promiscuous and multicast filter state in firmware memory.
- Exported helpers declared in `icssm_prueth.h` include packet descriptor parsing, RX packet copy, multicast bin updates, and multicast hash calculation.

## Control flow
Probe is DT-driven: it validates at least one available port, gets PRU0/PRU1 if corresponding ports exist, configures PRUSS GPI/MII_RT/XFR, requests PRUSS DRAM/shared RAM regions, allocates OCMC SRAM, initializes netdevs, obtains IEP, registers netdevs, then registers notifiers. Each netdev open copies any user-changed MAC from `ndev->dev_addr`, initializes host memory only once, configures per-port memory, initializes FDB when in switch mode, starts IEP and firmware, requests RX IRQ, enables NAPI, starts the PHY, and sets the firmware port-control byte. RX IRQ only disables the IRQ and schedules NAPI. NAPI walks host queues, parses buffer descriptors from shared RAM, copies packet bytes out of OCMC, updates ring read pointers, and re-enables the IRQ when budget is not exhausted. TX maps VLAN PCP to one of four firmware queues, pads the skb, checks ring space, copies bytes into OCMC, writes a length descriptor, advances the write pointer, and frees or defers the skb based on queue availability.

Bridge events drive mode changes. When both PRU ports are members of the same bridge, `offload_fwd_mark` is enabled and the driver restarts active netdevs into `PRUSS_ETHTYPE_SWITCH`; when no bridge members remain, it restarts them into dual EMAC mode. The switchdev notifier set is registered from this file but implemented in `icssm_switchdev.c`.

## State and persistence behavior
All persistent driver state is kernel runtime state: `struct prueth`, `struct prueth_emac`, PRUSS memories, OCMC buffers, PHY state, PRU remoteproc firmware state, notifier blocks, and NAPI/timer state. There is no on-disk persistence. Firmware-visible state lives in PRUSS DRAM/shared RAM and OCMC, including queue descriptors, read/write pointers, port status/control bytes, MAC address, multicast table, PTP control block, and switch FDB when enabled. `emac_configured` is a bitmask that coordinates shared initialization and firmware lifetime across two Linux netdevs. `br_members` and `hw_bridge_dev` track bridge offload eligibility.

## Dependencies and integration points
The file depends on Linux netdev, PHY, bridge, VLAN, multicast, notifier, NAPI, hrtimer, platform device, OF, PRUSS remoteproc, PRUSS memory, genalloc SRAM, syscon/regmap MII_RT, and ICSS IEP APIs. It shares constants and structures with `icssm_prueth.h`, `icssm_switch.h`, `icssm_prueth_switch.h`, `icssm_vlan_mcast_filter_mmap.h`, `icssg_mii_rt.h`, and `icss_iep.h`. External visible integration includes firmware files under `ti-pruss/*prueth-fw.elf` and `*prusw-fw.elf`, DT compatibles `ti,am57-prueth`, `ti,am4376-prueth`, and `ti,am3359-prueth`, and Linux bridge/switchdev offload.

## Risks and edge cases
- Several firmware-memory offsets and queue sizes are hard-coded; any firmware layout mismatch can corrupt queues or control fields.
- TX/RX rings are manually managed by pointer arithmetic over 16-bit descriptor offsets; off-by-one and wrap handling are critical.
- The mode-change path stops and reopens running netdevs; partial restart failure can leave ports in mixed operational state.
- Switch mode assumes both PRUs and both physical ports are available, while probe permits single-port operation.
- RX packet length validation drops malformed queues by advancing to the firmware write pointer; this avoids lockup but loses all queued packets in that queue.
- Multicast hash is a simple XOR masked by six bytes, so collisions are expected and can over-permit multicast traffic.
- Firmware boot/shutdown is coordinated by `emac_configured`; ordering bugs affect shared IEP and dual-PRU switch firmware lifetime.

## Test signals
Useful tests include DT probe success/failure for one-port and two-port nodes, `ip link set up/down` for each netdev in both EMAC and switch modes, bridge enslave/unenslave mode transitions, RX/TX traffic with VLAN PCP classes, queue-full TX retry behavior, multicast/promiscuous/allmulti changes, invalid or oversized RX descriptors from firmware, suspend/resume with running interfaces, firmware missing or boot failure, and resource unwind paths from probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth.h

## Purpose
This header defines the shared data model for the ICSSM PRU Ethernet driver. It describes PRU Ethernet modes, port/queue IDs, firmware names, memory regions, packet descriptor metadata, netdev-private per-port state, global PRUSS state, and prototypes shared by the EMAC, switch, and switchdev implementation files.

## Important APIs, types, and functions
- `enum pruss_ethtype` distinguishes EMAC, HSR, PRP, and switch firmware modes; this driver actively uses EMAC and switch mode.
- `PRUETH_IS_EMAC()` and `PRUETH_IS_SWITCH()` are common branch predicates over `prueth->eth_type`.
- `struct prueth_queue_desc` models firmware queue descriptors with read/write pointers, busy/status, max-fill, and overflow counters.
- `struct prueth_queue_info` maps a queue to OCMC buffer offsets and shared-RAM buffer descriptor offsets.
- `struct prueth_packet_info` is a decoded view of firmware buffer descriptor flags.
- `enum prueth_port`, `enum prueth_mac`, `enum prueth_port_queue_id`, and `enum prueth_queue_id` define host/MII ports and four priority queues.
- `struct prueth_emac` is per-netdev state: PRU pointer, PHY, queue descriptor bases, link settings, IRQ, queue selection, DRAM region, locks, timer, stats, multicast mask, and switch offload mark.
- `struct prueth` is device-wide state: PRUSS/PRU handles, memory regions, SRAM pool, MII_RT, IEP, firmware data, DT nodes, netdevs, bridge/FDB/notifier state, current Ethernet mode, OCMC size, configured-port bitmask, and bridge-member bitmask.
- Prototypes expose `icssm_parse_packet_info()`, `icssm_emac_rx_packet()`, multicast bin helpers, and multicast hash.

## Control flow
The header does not execute code, but it defines the state passed through the driver lifecycle. Probe fills `struct prueth`, netdev init fills each `struct prueth_emac`, open/stop mutates `emac_configured`, datapath functions consume queue descriptor and queue info structures, and switchdev code uses the shared `fdb_tbl`, bridge state, and notifier blocks.

## State and persistence behavior
The defined structures are in-memory only. Some fields are mirrors or pointers into firmware-owned PRUSS memory: queue descriptor bases, FDB table, DRAM/shared RAM regions, and OCMC buffer pools. `struct prueth_emac_stats` is a simple unsynchronized per-port software stats store read by `ndo_get_stats64`.

## Dependencies and integration points
The header imports Linux PHY/types, PRUSS driver and remoteproc PRUSS APIs, plus local ICSSM switch, PTP, and FDB-table headers. It is included by the main driver, switch implementation, and switchdev implementation, making it the central compile-time contract among ICSSM files.

## Risks and edge cases
- Recursive include coupling exists: `icssm_prueth.h` includes `icssm_prueth_fdb_tbl.h`, and the FDB header includes `icssm_prueth.h`; header guards prevent recursion but this increases coupling.
- Enum numeric values are assumed by array indexing and by `BIT(port_id)` bridge/configured masks.
- Stats are plain `u64` fields, unlike the u64_stats pattern used in NetCP; concurrent 32-bit readers may need attention depending on architecture expectations.
- Queue and memory structures must match firmware ABI exactly.

## Test signals
Compile coverage should catch structural drift. Runtime signals include correct port-to-queue mapping, correct `emac_configured` bit behavior when one or both ports are opened, multicast filtering through the exported helpers, and switchdev FDB use of `prueth->fdb_tbl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_fdb_tbl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_fdb_tbl.h

## Purpose
This header defines the firmware-shared forwarding database layout for ICSSM switch mode. The host driver and PRU firmware both view the same shared-RAM table, so the structures describe the exact index table, MAC table, STP state, flood-enable flags, and arbitration bytes.

## Important APIs, types, and functions
- `struct fdb_index_tbl_entry` maps an 8-bit hash bucket to a first MAC-table index and bucket entry count.
- `struct fdb_index_array` contains 256 bucket entries.
- `struct fdb_mac_tbl_entry` stores a MAC address, age, zero-based port, and packed `is_static`/`active` flags.
- `struct fdb_mac_tbl_array` contains 256 MAC entries.
- `struct fdb_stp_config` and `struct fdb_flood_config` provide per-port STP and flooding policy bytes.
- `struct fdb_arbitration` contains host and PRU lock bytes for shared table arbitration.
- `struct fdb_tbl` is the host-side collection of `__iomem` pointers to each firmware table section plus the host-maintained total entry count.

## Control flow
The header has no executable code. `icssm_prueth_switch.c` maps these structures onto offsets from `icssm_switch.h`, initializes flood flags and lock bytes, then uses the index and MAC arrays to add/delete/learn/purge FDB entries while coordinating with PRU locks.

## State and persistence behavior
FDB contents persist only while switch firmware and driver state are active. Actual entries live in PRUSS shared RAM; `struct fdb_tbl` holds host pointers and a software `total_entries` counter allocated during switch open and freed after switch shutdown when no EMAC remains configured.

## Dependencies and integration points
The file depends on Linux kernel/debugfs includes and local ICSSM definitions. Its struct sizes feed the shared-memory offsets in `icssm_switch.h`, so it is part of the firmware ABI. It is consumed by `icssm_prueth_switch.c` and `icssm_switchdev.c`.

## Risks and edge cases
- Bitfields and structure packing must stay ABI-compatible with firmware expectations.
- `total_entries` is host-side only; if firmware ages out entries independently, the host counter can diverge unless firmware behavior is constrained.
- The 8-bit XOR hash and fixed 256-entry MAC table bound scale and collision behavior.
- The host/PRU lock is a byte-level protocol; timeout or stale locks directly affect switchdev updates.

## Test signals
Exercise FDB insert/delete/learn/purge under traffic, full-table conditions, duplicate MAC updates, STP state changes, and concurrent firmware learning. Confirm structure sizes and offsets against firmware documentation or integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_fdb_tbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_ptp.h

## Purpose
This header defines ICSSM shared-RAM offsets and helper calculations for PTP/time-sync data exchanged with firmware. It covers RX/TX timestamp slots, notification bytes, domain and correction fields, time-sync compare/period control, single-step metadata, and small mode-control flags.

## Important APIs, types, and functions
- Offset macros define firmware locations for RX Sync/Pdelay timestamps, TX timestamp notifications, TX timestamps, correction fields, compare/period settings, link-local and E2E/UDP controls, previous timestamps, clock identity, and scratch memory.
- The anonymous enum defines PTP event indices: Sync, Delay Request, Delay Response, and count.
- `PRUETH_PTP_TS_SIZE`, notify size, and mask define record widths.
- `TIMESYNC_CTRL_BG_ENABLE` and `TIMESYNC_CTRL_FORCED_2STEP` describe control bits.
- `icssm_prueth_tx_ts_offs_get(port, event)` computes a TX timestamp offset for a port/event pair.
- `icssm_prueth_tx_ts_notify_offs_get(port, event)` computes the matching notification byte offset.

## Control flow
The header has only inline offset math. `icssm_prueth.c` uses the offsets in `icssm_ptp_dram_init()` to initialize correction, RCF, compare period, domain list, relay behavior, HSR tag mode, and E2E/UDP timestamping before starting firmware and IEP support.

## State and persistence behavior
PTP state is volatile firmware shared memory. The host writes initial values at interface open; firmware updates timestamp and notification fields at runtime. No persistent storage is involved.

## Dependencies and integration points
The macros rely on Linux `BIT()` being available through includers. The runtime integration point is the ICSS IEP driver used by `icssm_prueth.c`; firmware must interpret these offsets exactly.

## Risks and edge cases
- Offset overlap is high risk because fields are tightly packed and comments indicate byte sizes rather than C structures.
- The helper functions assume linear per-port/per-event layout starting at port 0.
- A firmware layout change without synchronized driver updates would break timestamp delivery or time-sync control.

## Test signals
Test interface open initializes expected shared-RAM values; PTP event timestamp offsets produce the expected P1/P2 slots; hardware timestamp traffic should produce notification byte changes and valid timestamp reads in firmware/driver integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_switch.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_switch.c

## Purpose
This file implements ICSSM switch-mode support layered under the main PRU Ethernet netdev driver. It defines switch queue layouts, initializes switch host/port memory tables, manages the firmware-shared FDB, schedules asynchronous FDB learning/purge work, and boots/shuts down both PRUs with switch firmware.

## Important APIs, types, and functions
- `sw_queue_infos` is exported and maps host/MII queues to OCMC and descriptor offsets for switch mode.
- `rx_queue_infos` maps RX contexts for host and physical ports.
- `icssm_prueth_sw_fdb_tbl_init()`, `icssm_prueth_sw_init_fdb_table()`, and `icssm_prueth_sw_free_fdb_table()` allocate/map/free host FDB state.
- `icssm_prueth_sw_fdb_spin_lock()` and `_unlock()` implement host/PRU arbitration over shared RAM lock bytes.
- FDB helpers implement hash, search, open-slot discovery, insertion point selection, slot shifting, index-table repair, insert, delete, and purge.
- `icssm_prueth_sw_fdb_add()`, `_del()`, `_learn_fdb()`, and `_purge_fdb()` are called from switchdev and RX datapath paths.
- `icssm_prueth_sw_hostconfig()`, `icssm_prueth_sw_port_config()`, and `icssm_prueth_sw_emac_config()` program firmware memory for switch operation.
- `icssm_prueth_sw_boot_prus()` and `icssm_prueth_sw_shutdown_prus()` manage dual-PRU switch firmware lifetime.

## Control flow
When switch mode opens, the main driver initializes host memory with `icssm_prueth_sw_hostconfig()`, then `icssm_prueth_sw_emac_config()` configures physical port contexts. The first switch-mode open maps PRU constant tables C28/C30 to shared RAM and OCMC. `icssm_prueth_sw_init_fdb_table()` allocates the host FDB object and points each subtable at fixed shared-RAM offsets; flood-to-host and flood-to-ports bits are enabled.

FDB insert locks against firmware, rejects local port MAC addresses, hashes the MAC, establishes a bucket if empty, finds sorted insertion point, shifts neighboring entries when necessary, writes MAC/age/port/static/active flags, increments bucket and total counts, and unlocks. Delete locks, searches the hash bucket, shifts remaining bucket entries left, clears active on the bucket tail, decrements counts, and unlocks. Learning and purge are deferred through `system_long_wq` using held netdev references; RX schedules learning when firmware reports source lookup failure.

Firmware boot is all-or-nothing for switch mode: PRU0 firmware is set/booted first, PRU1 second, and PRU0 is shut down if PRU1 setup fails. Shutdown only runs once all ports are no longer configured.

## State and persistence behavior
Switch state is volatile. Queue tables and FDB tables live in PRUSS DRAM/shared RAM and OCMC. `prueth->fdb_tbl` is heap state pointing into shared RAM; `total_entries` is maintained by host code. Deferred FDB work owns a held netdev reference and a copy of the MAC/event until the work item completes.

## Dependencies and integration points
The file integrates with `icssm_prueth.c` for open/stop, TX/RX queue selection, RX learning, firmware lifecycle, and mode changes. It integrates with `icssm_switchdev.c` for static FDB and STP events. It depends on Linux remoteproc, etherdevice helpers, switchdev notifier structs, workqueues, and the local firmware ABI constants in `icssm_switch.h` and `icssm_prueth_fdb_tbl.h`.

## Risks and edge cases
- FDB table manipulation is complex: sorted buckets are stored in one global MAC array, so left/right shifts must update affected bucket indexes exactly.
- `icssm_prueth_sw_do_purge_fdb()` clears dynamic entries without compacting buckets, which may leave inactive holes; insertion/search behavior must be verified against this.
- Lock timeout is only 10 microseconds worth of polling; busy firmware can cause transient offload failure.
- `kzalloc_obj(..., GFP_ATOMIC)` learning work from RX can fail under pressure, silently losing learned entries except for WARN.
- Switch mode requires both PRUs; single-port configurations with switch requested are risky.
- FDB `port` is stored as `port_id - 1`; enum changes or invalid port IDs would corrupt firmware interpretation.

## Test signals
Run bridge offload with learning traffic, static FDB add/delete, duplicate MAC on same and different ports, full 256-entry table, hash collisions, purge after STP state change, PRU lock timeout injection, PRU1 firmware boot failure unwind, and traffic validation after repeated EMAC/switch mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_switch.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_switch.h

## Purpose
This header exposes the switch-mode service boundary used by the main ICSSM netdev driver and switchdev code. It declares STP accessors, queue info, FDB management, host/port configuration, and dual-PRU firmware lifecycle helpers.

## Important APIs, types, and functions
- `icssm_prueth_sw_set_stp_state()` and `_get_stp_state()` read/write per-port STP state in the shared FDB area.
- `sw_queue_infos` exposes switch queue memory mapping to the TX datapath.
- FDB entry points include init/free, immediate static add/del, deferred learning, deferred purge, and direct purge.
- Configuration entry points include `icssm_prueth_sw_hostconfig()` and `icssm_prueth_sw_emac_config()`.
- Firmware entry points include `icssm_prueth_sw_boot_prus()` and `icssm_prueth_sw_shutdown_prus()`.

## Control flow
The header is invoked from `icssm_prueth.c` during open, stop, TX enqueue, and bridge mode switching; from `icssm_switchdev.c` for STP and FDB events; and from RX processing for source learning.

## State and persistence behavior
The declared functions operate on `struct prueth` and `struct prueth_emac`, mutating PRUSS shared memory, OCMC/DRAM queue context, heap FDB state, and remoteproc firmware state. No persistent state exists beyond active driver lifetime.

## Dependencies and integration points
It includes Linux switchdev and local ICSSM PRU/FDB/switchdev headers. It is the compile-time glue between the generic netdev implementation and switch-specific implementation.

## Risks and edge cases
- `extern const struct prueth_queue_info sw_queue_infos[][4]` hard-codes queue count as 4 rather than `NUM_QUEUES`, so changes to queue count require coordinated updates.
- Callers must only use switch APIs when the device is in switch-capable mode and both required resources exist.
- FDB pointers may be NULL when an interface is down; switchdev callers check for this in implementation.

## Test signals
Build-time coverage for prototypes, runtime bridge enslave/unenslave, switch TX queue selection, STP state update, static FDB add/delete, and clean shutdown after one or both ports stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_switch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switch.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switch.h

## Purpose
This header is the memory-map and descriptor ABI for ICSSM EMAC and switch firmware. It defines queue sizes, descriptor bit fields, PRUSS DRAM/shared-RAM offsets, OCMC buffer offsets, and switch FDB offsets. The driver uses these macros to program firmware-visible memory exactly.

## Important APIs, types, and functions
- Basic sizes: `SWITCH_BUFFER_SIZE`, `ICSS_BLOCK_SIZE`, `BD_SIZE`, `NUM_QUEUES`, host and physical queue depths.
- Buffer descriptor masks/shifts describe packet length, port, broadcast, error, timestamp, lookup success, flood, shadow, and HSR bits.
- DRAM offsets include statistics, storm prevention, PHY speed, port status/control, MAC address, RX interrupt status, and STP invalid state.
- Switch DRAM offsets describe queue descriptors, collision descriptors, collision status, interface/port MAC addresses, size/offset/descriptor tables, and RX/TX contexts.
- EMAC offsets describe TTS and host queue context locations.
- Shared-RAM offsets define host queue descriptors, size/offset tables, promiscuous mode bits, and buffer descriptor pool layout.
- OCMC offsets define buffer regions for host and MII queues.
- FDB offsets define shared-RAM locations and sizes for index table, MAC table, per-port STP config, flood flags, and locks.

## Control flow
This header has no executable control flow. It drives control flow indirectly: queue init functions copy `queue_descs` and queue info into the offsets declared here; TX/RX datapath uses descriptor bit masks; switch FDB code maps typed `__iomem` structures onto FDB offsets.

## State and persistence behavior
All defined addresses refer to volatile PRUSS DRAM/shared RAM or OCMC memory. Values are initialized on driver open and consumed/mutated by firmware during packet processing. No on-disk persistence exists.

## Dependencies and integration points
The header is consumed by `icssm_prueth.h`, `icssm_prueth.c`, and `icssm_prueth_switch.c`. It assumes local FDB structure definitions are visible for `sizeof(struct fdb_...)` macros through include ordering. It is tightly coupled with TI PRU firmware.

## Risks and edge cases
- Most constants are firmware ABI. Renaming, resizing, or reordering can cause runtime memory corruption without compile errors.
- The descriptor comments list overlapping semantic bits inherited from multiple protocols; code only decodes some fields.
- Host queue size macros and buffer offsets must fit in the allocated OCMC size, which differs for AM33xx due to an 8 KiB reserved region.
- `COL_QUEUE_SIZE` is zero while collision descriptors still exist; firmware expectations should be checked.

## Test signals
Validation should include compile-time or runtime offset assertions against firmware ABI, traffic at maximum supported frame size, queue wrap and overflow, descriptor flag parsing, EMAC promiscuous bit updates, and switch FDB shared-memory mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switchdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switchdev.c

## Purpose
This file connects ICSSM switch mode to Linux switchdev. It handles STP state changes, static FDB add/delete notifications, host MDB add/delete notifications, and registration of normal and blocking switchdev notifiers.

## Important APIs, types, and functions
- `struct icssm_sw_event_work` carries deferred FDB event data, a held netdev reference, and a copied `switchdev_notifier_fdb_info`.
- `icssm_prueth_sw_set_stp_state()` and `_get_stp_state()` access shared-RAM STP state through `prueth->fdb_tbl`.
- `icssm_prueth_sw_attr_set()` handles `SWITCHDEV_ATTR_ID_PORT_STP_STATE`; state changes trigger dynamic FDB purge.
- `icssm_prueth_sw_switchdev_event()` handles nonblocking switchdev events and defers FDB add/delete work.
- `icssm_sw_event_work()` performs static FDB add/delete under RTNL and calls `SWITCHDEV_FDB_OFFLOADED` after successful user-added FDB offload.
- `icssm_prueth_switchdev_obj_add()` and `_del()` update firmware multicast filter bins for host MDB entries.
- `icssm_prueth_sw_blocking_event()` handles blocking object and attr updates.
- `icssm_prueth_sw_register_notifiers()` and `_unregister_notifiers()` install/remove notifier blocks stored in `struct prueth`.

## Control flow
For STP attr events, switchdev invokes the handler and the driver writes the new state into the FDB shared-memory STP byte. If the state changed, dynamic FDB entries are purged asynchronously. For FDB events, the notifier allocates work from atomic context, copies the notifier payload and MAC address, holds the netdev, and schedules `system_long_wq`. The worker runs under RTNL, ignores events when the interface/FDB is down, ignores non-user-added or local FDB additions, calls the switch FDB implementation, signals offload for accepted additions, then frees copied memory and drops the netdev reference. MDB events hash the multicast address using the EMAC hash helper and allow/disallow the corresponding firmware multicast bin, avoiding disallow when another bridge multicast address collides in the same bin.

## State and persistence behavior
State changes affect firmware-shared FDB/STP/multicast table memory and queued work items. Work items persist only until processed. Notifier registrations persist for the platform device lifetime and are removed in driver remove.

## Dependencies and integration points
The file depends on Linux switchdev, workqueue, netdevice reference tracking, RTNL, and local ICSSM PRU/FDB/switch APIs. It is called from the registration path in `icssm_prueth.c` and calls into `icssm_prueth_switch.c` and multicast helpers in `icssm_prueth.c`.

## Risks and edge cases
- FDB event allocation uses GFP_ATOMIC; failure returns `NOTIFY_BAD` for allocation errors and can drop offload updates.
- The FDB worker assumes copied `fdb_info.addr` is valid and frees it after use.
- MDB delete handles hash collisions only against bridge multicast addresses, not necessarily all port-local multicast state.
- STP and FDB paths no-op when `prueth->fdb_tbl` is NULL, so down interfaces can miss offload state transitions.
- `icssm_prueth_sw_set_stp_state()` uses `port - 1` to choose port1/port2 state; invalid port values would write the wrong field.

## Test signals
Use Linux bridge tests for STP state transitions, static FDB add/delete, `bridge fdb show` offloaded flag, MDB joins/leaves, multicast hash collision cases, notifier registration/unregistration during driver remove, and event delivery while ports are down/up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switchdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switchdev.h

## Purpose
This small header declares the ICSSM switchdev notifier interface and port-device predicate shared between the main driver and switchdev implementation.

## Important APIs, types, and functions
- `icssm_prueth_sw_register_notifiers(struct prueth *prueth)` registers switchdev notifier blocks.
- `icssm_prueth_sw_unregister_notifiers(struct prueth *prueth)` unregisters them.
- `icssm_prueth_sw_port_dev_check(const struct net_device *ndev)` identifies ICSSM ports eligible for switchdev handling.

## Control flow
`icssm_prueth.c` calls register during probe after netdev registration and unregister during remove. Switchdev helper calls use the predicate to filter events to ICSSM devices with L2 firmware offload capability.

## State and persistence behavior
The header itself stores no state. The declared functions mutate notifier blocks in `struct prueth` and inspect netdev features/ops.

## Dependencies and integration points
It includes `icssm_prueth.h`, so users gain the ICSSM core type definitions. It is included by `icssm_prueth_switch.h` and implemented by `icssm_switchdev.c`.

## Risks and edge cases
- The predicate is central to avoiding unrelated switchdev events; an overly broad match could mis-handle another netdev, while an overly narrow match disables offload.
- Include coupling with the full ICSSM header increases rebuild scope.

## Test signals
Probe/remove should register and unregister without leaks. Bridge and switchdev operations on non-ICSSM devices should be ignored, while ICSSM offload-capable ports should accept relevant events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switchdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_vlan_mcast_filter_mmap.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_vlan_mcast_filter_mmap.h

## Purpose
This header defines firmware memory-map constants for ICSSM VLAN and multicast filtering. The main EMAC driver and switchdev MDB handlers use these offsets and values to program multicast hash bins and filter control bytes.

## Important APIs, types, and functions
- Multicast control values enable/disable filtering and allow/disallow host receive for a hash bin.
- Size macros define the multicast table, hash mask, control byte, override status, and drop counter widths.
- Offset macros define multicast mask, control, override status, drop counter, and table base in PRU DRAM.
- LRE multicast offsets define an alternate control/mask/table region.
- VLAN offsets define a 512-byte 4096-bit VLAN table, control bitmap, drop counter, and LRE switch VLAN filter locations.
- VLAN control bit macros describe enable, untagged, priority-tagged, and service-VLAN flow behavior.
- VLAN ID range and add/remove command constants define firmware command values.

## Control flow
The header has no functions. `icssm_emac_ndo_set_rx_mode()` writes the multicast control byte, resets the table, writes the hash mask, and toggles bins based on netdev and bridge multicast addresses. `icssm_switchdev.c` updates bins for host MDB add/delete events.

## State and persistence behavior
The constants address volatile PRU DRAM/SRAM regions. Filter state is reinitialized during RX mode changes and does not survive driver shutdown or firmware restart.

## Dependencies and integration points
The header is consumed by ICSSM driver code and must match firmware layout. It has no Linux include dependencies beyond what includers provide.

## Risks and edge cases
- The closing comment names a different guard (`ICSS_MULTICAST_FILTER_MM_H`) than the actual guard; harmless but confusing.
- A simple 256-bin multicast hash can collide, causing over-allow or careful disallow behavior.
- VLAN constants are defined but not substantially exercised by the researched files, so dead or future ABI drift is possible.

## Test signals
Test multicast receive filtering with no multicast addresses, specific multicast joins, allmulti, promiscuous mode, bridge MDB add/delete, hash collisions, and firmware drop counter changes. VLAN filtering tests should verify table bit layout if implementing VLAN controls against these macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_vlan_mcast_filter_mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/k3-cppi-desc-pool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/k3-cppi-desc-pool.c

## Purpose
This file implements a small exported API for allocating fixed-size TI K3 CPPI5 descriptors from a coherent DMA block. It wraps `dma_alloc_coherent()` and a `gen_pool` so clients can allocate/free descriptors by CPU address, translate CPU/DMA addresses, and attach per-descriptor software metadata.

## Important APIs, types, and functions
- `struct k3_cppi_desc_pool` stores the owning device, DMA base, CPU base, rounded descriptor size, memory size, descriptor count, gen_pool, and sideband `desc_infos`.
- `k3_cppi_desc_pool_create_name()` allocates the pool object, rounds descriptor size to a power of two, creates a named gen_pool, allocates sideband metadata array, allocates coherent DMA memory, and adds it to the gen_pool.
- `k3_cppi_desc_pool_destroy()` warns if descriptors are still allocated, frees coherent memory, metadata, gen_pool, and the pool.
- `k3_cppi_desc_pool_virt2dma()` and `_dma2virt()` translate by base-offset arithmetic.
- `k3_cppi_desc_pool_alloc()` and `_free()` allocate and free one descriptor-sized block.
- `k3_cppi_desc_pool_avail()`, `_desc_size()`, `_cpuaddr()`, `_desc_info_set()`, and `_desc_info()` expose pool metadata and sideband storage.

## Control flow
Creation is fail-unwind structured: allocate pool, duplicate name, create gen_pool, allocate metadata array, allocate coherent memory, add memory to gen_pool, return pool. Failure paths free in reverse order. Allocation/free are direct gen_pool calls. Destroy checks for leaked descriptors by comparing gen_pool total and available bytes before freeing resources.

## State and persistence behavior
State is entirely in kernel memory and coherent DMA memory. Descriptors persist until freed or until the pool is destroyed. The `desc_infos` array persists sideband pointers per descriptor index but bounds are not checked by this API.

## Dependencies and integration points
The file exports GPL symbols for other kernel drivers. It depends on Linux device, DMA mapping, genalloc, err, and kernel helpers. The paired header exposes the opaque pool type and API. It is meant for K3 Ethernet/UDMA-style clients that need CPPI5 descriptors.

## Risks and edge cases
- Descriptor size is rounded up to a power of two; clients must use the returned size when computing indices.
- Address translation assumes the passed address/DMA belongs to the pool and performs no range checking.
- `desc_info_set()` and `desc_info()` do not validate `desc_idx`.
- Destroy warns but still frees if descriptors are outstanding.
- Pointer arithmetic on `void *` is compiler extension style used by the kernel; misuse outside kernel conventions would be unsafe.

## Test signals
Create/destroy with normal and named pools, allocation until exhaustion, free/reallocate cycles, descriptor size rounding, virt-to-DMA and DMA-to-virt round trips, outstanding allocation warning on destroy, and metadata set/get for valid indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/k3-cppi-desc-pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/k3-cppi-desc-pool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/k3-cppi-desc-pool.h

## Purpose
This header declares the opaque CPPI5 descriptor pool API implemented by `k3-cppi-desc-pool.c`. It is the public contract for drivers that allocate fixed-size coherent DMA descriptors.

## Important APIs, types, and functions
- `struct k3_cppi_desc_pool` is opaque to callers.
- `k3_cppi_desc_pool_create_name()` creates a named pool; `k3_cppi_desc_pool_create()` is a convenience macro using the device name.
- Destroy, CPU/DMA translation, allocation/free, available count, descriptor size, CPU base address, and sideband descriptor-info accessors are declared.

## Control flow
Callers create a pool, allocate descriptors, translate addresses as needed for hardware rings, optionally store sideband info by descriptor index, free descriptors, then destroy the pool.

## State and persistence behavior
The header owns no state. The implementation maintains coherent DMA memory and metadata until destroy.

## Dependencies and integration points
It includes Linux device and types headers and is consumed by TI networking or DMA clients needing CPPI descriptor pools.

## Risks and edge cases
- Because the pool is opaque, callers rely on API discipline for valid addresses and descriptor indices; the implementation does not enforce all bounds.
- The create macro hides the name argument, which is convenient but can make multi-pool diagnostics less clear unless callers use `_create_name()`.

## Test signals
Compile users against the declarations, verify symbol exports, and run pool allocation/free/translation tests through a client driver or KUnit-style harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/k3-cppi-desc-pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp.h

## Purpose
This is the local interface for the TI Keystone NetCP core. It defines the netcp interface state, module plugin contract, TX pipe abstraction, packet metadata passed through ordered hooks, address tracking, statistics, hardware link-mode constants, and exported core APIs used by NetCP submodules.

## Important APIs, types, and functions
- `struct netcp_tx_pipe` describes a DMA TX path, including queue/channel names, queue ID, target switch port, and tag-info behavior.
- `struct netcp_addr` and `enum netcp_addr_type` track broadcast, device, unicast, multicast, and promiscuous wildcard addresses with mark bits.
- `struct netcp_stats` uses `u64_stats_sync` and `u64_stats_t` for RX/TX packets and bytes plus 32-bit errors/drops.
- `struct netcp_intf` is the per-netdev core state: DMA queues, pools, NAPI, hook lists, module-private list, address list, runtime flags, lock, device pointers, and queue depth configuration.
- `struct netcp_packet` is the object passed through RX/TX hooks, containing skb, descriptor EPIB/PS data, flags, selected TX pipe, timestamp callback, and context.
- `netcp_push_psdata()` reserves protocol-specific words at the tail of the PS data array.
- `netcp_align_psdata()` reports padding needed for a desired byte alignment.
- `struct netcp_module` is the submodule plugin interface: probe/remove once per device, attach/release per netdev, open/close, address/VLAN updates, ioctl, RX mode, and hardware timestamp get/set.
- Exported prototypes register/unregister modules and hooks, manage TX pipes, and declare SGMII/XGBE helpers.

## Control flow
NetCP platform probe creates `struct netcp_intf` objects. Submodules register via `netcp_register_module()`, are probed per device, attached per interface via phandles, and can register RX/TX hooks. During TX, hooks inspect and mutate `struct netcp_packet`, select a `netcp_tx_pipe`, and populate PS/EPIB/timestamp behavior. During RX, hooks process packet metadata before the core delivers the skb to the network stack. Address/VLAN/RX-mode changes are fanned out to attached modules.

## State and persistence behavior
All state is kernel runtime state. The interface object owns lists of modules, hooks, and address records. DMA queues/pools/channels are opened on netdev open and closed on stop. Stats persist for the netdev lifetime.

## Dependencies and integration points
The header depends on Linux netdevice, TI knav DMA, and u64 stats APIs. It is implemented by `netcp_core.c` and used by Keystone Ethernet switch/SGMII/XGBE modules.

## Risks and edge cases
- The packet hook contract is powerful but implicit: TX must be claimed by exactly one hook through `p_info.tx_pipe`.
- PS data helpers reserve from the end of a fixed word array; hook order must be coordinated.
- Several implementation paths store kernel pointers in 32-bit descriptor software words, noted as not working on 64-bit machines.
- Module registration order and primary-module behavior affect when interfaces become registered.

## Test signals
Compile submodules against the module API, register/unregister modules before and after platform probe, TX hook ordering and TX pipe selection, RX hook rejection, PS data alignment/push bounds, address list fanout, VLAN fanout, and hardware timestamp delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_core.c

## Purpose
This file implements the TI Keystone NetCP core platform driver and netdev framework. It manages NetCP module registration/probing/attachment, ordered RX/TX hook lists, Navigator DMA/QMSS descriptor queues, NAPI RX/TX completion, netdev operations, address/VLAN fanout to modules, timestamp delegation, interface creation from DT, and platform probe/remove.

## Important APIs, types, and functions
- Internal device/module structs: `struct netcp_device`, `struct netcp_inst_modpriv`, `struct netcp_intf_modpriv`, and `struct netcp_tx_cb`.
- Descriptor helpers get/set packet, descriptor, original-buffer, software-word, EPIB, and PS data fields with little-endian conversion where needed.
- Module APIs: `netcp_register_module()`, `netcp_unregister_module()`, `netcp_module_probe()`, `netcp_release_module()`, and `netcp_module_get_intf_data()`.
- Hook APIs: `netcp_register_txhook()`, `_unregister_txhook()`, `netcp_register_rxhook()`, and `_unregister_rxhook()`, preserving ascending order.
- RX datapath: `netcp_allocate_rx_buf()`, `netcp_rxpool_refill()`, `netcp_process_one_rx_packet()`, `netcp_rx_poll()`, `netcp_rx_notify()`, and cleanup helpers.
- TX datapath: `netcp_tx_map_skb()`, `netcp_tx_submit_skb()`, `netcp_ndo_start_xmit()`, `netcp_process_tx_compl_packets()`, `netcp_tx_poll()`, and `netcp_tx_notify()`.
- TX pipe exports: `netcp_txpipe_init()`, `_open()`, and `_close()`.
- Netdev ops: open/stop, start_xmit, set_rx_mode, ioctl, stats, VLAN add/delete, TX timeout, mqprio setup, and hardware timestamp get/set.
- Platform: `netcp_create_interface()`, `netcp_delete_interface()`, `netcp_probe()`, `netcp_remove()`, and OF match `ti,netcp-1.0`.

## Control flow
Platform probe defers until knav DMA and QMSS are ready, enables runtime PM, creates interfaces from `netcp-interfaces`, links the device into the global device list, then probes any already registered modules under `netcp_modules_lock`. Module registration adds the module to the global list and probes it against existing devices; module probe looks for a matching DT child under `netcp-devices`, calls module probe, attaches it to each interface that references the module by phandle, and registers netdevs once a primary module is available.

Netdev open creates Navigator resources: RX/TX descriptor pools, TX completion queue, RX completion queue, RX free descriptor queues, notifiers, and RX DMA channel. It then calls each attached module open, enables NAPI and queue notifications, refills RX FDQs, and wakes TX queues. Stop halts queues/carrier, clears address marks and fanout deletions, disables notifications/NAPI, calls module close, recycles RX and TX descriptors, validates TX pool count, and frees Navigator resources.

TX maps skb linear and fragment buffers into one or more DMA descriptors, runs ordered TX hooks, requires a hook to select a `netcp_tx_pipe`, writes PS data/EPIB/return queue/target port info, stores skb/timestamp callback in descriptor/SKB control state, maps the descriptor, pushes it to the DMA queue, and pauses subqueues when descriptors fall below threshold. TX completion pops completion descriptors, unmaps/free descriptor chains, invokes timestamp callback, wakes subqueues if descriptor count recovers, updates stats, and frees skb.

RX refills FDQs with primary buffers and secondary page buffers. RX notify schedules NAPI. RX NAPI pops descriptors, builds an skb from the primary buffer, attaches page frags for chained descriptors, trims FCS for older hardware, runs RX hooks, updates stats, delivers with `netif_receive_skb()`, and refills FDQs.

## State and persistence behavior
Global runtime state includes `netcp_devices`, `netcp_modules`, and `netcp_modules_lock`. Per-device state tracks interface and module-private lists. Per-interface state holds DMA queues/pools/channels, NAPI instances, hook lists, address records, module-private attachments, stats, and DT-derived queue/pool configuration. Resources are created on probe/interface creation or netdev open and are destroyed on stop/remove. No disk persistence is present.

## Dependencies and integration points
The file depends on Linux platform, OF, PM runtime, netdevice, VLAN, tc mqprio, DMA mapping, NAPI, TI knav QMSS and DMA APIs, and local `netcp.h`. It exports GPL symbols for NetCP submodules and declares a platform driver for `ti,netcp-1.0`.

## Risks and edge cases
- The code stores virtual pointers in 32-bit descriptor `sw_data` fields, with explicit warnings that this will not work on 64-bit machines.
- In RX, `pkt_sz` is initialized to zero and masked without reading descriptor packet length first, so the packet-size mismatch debug comparison appears ineffective or suspicious.
- DMA mapping direction in RX allocation uses `DMA_TO_DEVICE` for buffers that are later unmapped with `DMA_FROM_DEVICE`; this deserves careful verification against the target DMA API expectations.
- Module lifecycle is order-sensitive; primary-module registration controls netdev registration.
- TX frag-list is unsupported and rejected after some mapping work, so unwind paths must remain correct.
- Address list updates call module callbacks while holding `netcp->lock`; callback behavior must avoid deadlocks.
- `netcp_delete_interface()` calls `unregister_netdev()` even if registration may not have happened unless interface creation/probe sequencing guarantees it.

## Test signals
Test probe with missing DT properties and deferred DMA/QMSS readiness; module registration before/after platform probe; primary-module delayed registration; netdev open/stop resource allocation and unwind; RX buffer refill and chained RX packets; TX linear, fragmented, and frag-list skb paths; TX completion and timeout recovery; hook ordering/rejection; address/promiscuous/multicast fanout; VLAN add/delete; hwtstamp get/set delegation; runtime PM remove; and 64-bit build/static analysis for descriptor pointer truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_core.c -->
