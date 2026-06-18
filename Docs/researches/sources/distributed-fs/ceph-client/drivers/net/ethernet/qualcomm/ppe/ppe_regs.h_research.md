<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_regs.h

## Purpose
`ppe_regs.h` is the hardware register and table definition header for the Qualcomm IPQ PPE driver. It names register/table bases, entry counts, increments, bit fields, and helper macros for BM, QM, scheduler, service-code, RSS, VLAN, bridge, port, L2, counter, and drop-count blocks.

## Important APIs, Types, and Data
- Register/table groups cover BM scheduler/drop/flow control, RSS hash, service-code tables, egress VLAN/bridge, VSI, MRU/MTU, L2 virtual ports, RX/TX/drop counters, tunnel/parser counters, scheduler L0/L1 tables, ring queue maps, enqueue/dequeue controls, admission-control queues/groups, and multicast/unicast drop counters.
- Uses `GENMASK()`, `BIT()`, and `FIELD_MODIFY()` helper macros to encode multiword tables.
- Address helper macros such as `PPE_CPU_PORT_MULTICAST_FORCE_DROP_CNT_TBL_ADDR()` encode table layout for debugfs.

## Control Flow
The header has no runtime flow. It provides compile-time constants consumed by `ppe_config.c` and `ppe_debugfs.c`.

## State and Persistence
No software state is owned here. The definitions describe persistent hardware state in the PPE MMIO region.

## Dependencies and Integration Points
Includes `linux/bitfield.h`. It must remain consistent with `ppe.c` regmap access ranges, `ppe_config.c` programming logic, and `ppe_debugfs.c` counter scanning.

## Risks and Edge Cases
- Incorrect address, increment, or entry-count definitions can make regmap access fail or corrupt unrelated hardware tables.
- Multiword `FIELD_MODIFY()` macros depend on callers passing sufficiently large arrays.
- Counter table sizes differ by subsystem; using the wrong size type misreads or clears counters.
- Some hardware comments describe reserved or unspecified values; enum/table users must preserve numeric positions.

## Test Signals
Compile-time use by all PPE objects, successful regmap writes during `ppe_hw_config()`, valid debugfs counter reads, and hardware traffic counters matching expected table indices are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_regs.h -->
