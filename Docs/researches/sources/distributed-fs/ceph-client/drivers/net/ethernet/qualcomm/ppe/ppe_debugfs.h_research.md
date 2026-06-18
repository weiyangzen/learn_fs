<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.h

## Purpose
`ppe_debugfs.h` declares the PPE debugfs setup and teardown hooks.

## Important APIs, Types, and Functions
- Includes `ppe.h` for `struct ppe_device`.
- Declares `ppe_debugfs_setup(struct ppe_device *ppe_dev)`.
- Declares `ppe_debugfs_teardown(struct ppe_device *ppe_dev)`.

## Control Flow
No control flow exists in the header. The platform driver calls setup after hardware config and teardown during remove.

## State and Persistence
No state is owned here; the functions mutate `ppe_device::debugfs_root` and debugfs entries in the implementation.

## Dependencies and Integration Points
Integrates `ppe.c` with `ppe_debugfs.c` while keeping debugfs details out of the platform driver.

## Risks and Edge Cases
The header assumes `ppe.h` is sufficient for the device type. Any future debugfs build option split would need stubs or conditional declarations.

## Test Signals
Successful PPE build/link and visible debugfs files after probe validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.h -->
