# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth.h

## Purpose
This header defines the shared data model for the ICSSM PRU Ethernet driver. It describes PRU Ethernet modes, port/queue IDs, firmware names, memory regions, packet descriptor metadata, netdev-private per-port state, global PRUSS state, and prototypes shared by the EMAC, switch, and switchdev implementation files.

## Important APIs, types, and functions
- `enum pruss_ethtype` distinguishes EMAC, HSR, PRP, and switch firmware modes; this driver actively uses EMAC and switch mode.
- `PRUETH_IS_EMAC()` and `PRUETH_IS_SWITCH()` are common branch predicates over `prueth->eth_type`.
- `struct prueth_queue_desc` models firmware queue descriptors with read/write pointers, busy/status, max-fill, and overflow counters.
- `struct prueth_queue_info` maps a queue to OCMC buffer offsets and shared-RAM buffer descriptor offsets.
- `struct prueth_packet_info` is a decoded view of firmware buffer descriptor flags.
- `struct prueth_emac` is per-netdev state: PRU pointer, PHY, queue descriptor bases, link settings, IRQ, queue selection, DRAM region, locks, timer, stats, multicast mask, and switch offload mark.
- `struct prueth` is device-wide state: PRUSS/PRU handles, memory regions, SRAM pool, MII_RT, IEP, firmware data, DT nodes, netdevs, bridge/FDB/notifier state, current Ethernet mode, OCMC size, configured-port bitmask, and bridge-member bitmask.

## Control flow
The header does not execute code, but it defines the state passed through the driver lifecycle. Probe fills `struct prueth`, netdev init fills each `struct prueth_emac`, open/stop mutates `emac_configured`, datapath functions consume queue descriptor and queue info structures, and switchdev code uses the shared `fdb_tbl`, bridge state, and notifier blocks.

## State and persistence behavior
The defined structures are in-memory only. Some fields are mirrors or pointers into firmware-owned PRUSS memory: queue descriptor bases, FDB table, DRAM/shared RAM regions, and OCMC buffer pools. `struct prueth_emac_stats` is a simple unsynchronized per-port software stats store read by `ndo_get_stats64`.

## Dependencies and integration points
The header imports Linux PHY/types, PRUSS driver and remoteproc PRUSS APIs, plus local ICSSM switch, PTP, and FDB-table headers. It is included by the main driver, switch implementation, and switchdev implementation, making it the central compile-time contract among ICSSM files.

## Risks and edge cases
- Recursive include coupling exists between the PRU Ethernet and FDB headers; header guards prevent recursion but increase coupling.
- Enum numeric values are assumed by array indexing and by `BIT(port_id)` bridge/configured masks.
- Stats are plain `u64` fields, unlike the u64_stats pattern used in NetCP.
- Queue and memory structures must match firmware ABI exactly.

## Test signals
Compile coverage should catch structural drift. Runtime signals include correct port-to-queue mapping, correct `emac_configured` bit behavior when one or both ports are opened, multicast filtering through the exported helpers, and switchdev FDB use of `prueth->fdb_tbl`.
