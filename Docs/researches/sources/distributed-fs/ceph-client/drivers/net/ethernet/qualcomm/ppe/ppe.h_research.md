<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.h

## Purpose
`ppe.h` defines the core private device structure shared by the PPE platform, configuration, and debugfs files.

## Important APIs, Types, and Data
- Forward declares `struct device`, `struct regmap`, and `struct dentry`.
- `struct ppe_device` stores the kernel device, regmap, PPE clock rate, number of ports, debugfs root, ICC path count, and a flexible counted `icc_paths[]` array.

## Control Flow
No runtime flow exists. The header defines shared state layout.

## State and Persistence
`struct ppe_device` is allocated at probe and persists until device removal. The flexible ICC path array is allocated with `struct_size()` according to the platform driver's path count.

## Dependencies and Integration Points
The header includes interconnect definitions and is consumed by `ppe.c`, `ppe_config.c`, `ppe_debugfs.c`, and their companion headers.

## Risks and Edge Cases
The flexible array depends on correct allocation sizing and `num_icc_paths`. Any future per-SoC port/count differences need fields initialized before configuration helpers consume them.

## Test Signals
Build checks for `__counted_by()` support and runtime probe with the expected number of ICC paths validate the structure contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.h -->
