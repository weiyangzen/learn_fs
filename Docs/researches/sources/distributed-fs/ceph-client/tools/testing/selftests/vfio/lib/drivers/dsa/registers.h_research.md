<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/registers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/registers.h

## Purpose
Defines Intel IDXD/DSA register offsets, capability bitfields, command/status enums, workqueue/group config structures, descriptor error records, and device IDs.

## Important APIs, Types, and Functions
PCI_DEVICE_ID_INTEL_DSA_*, union gen_cap_reg/wq_cap_reg/group_cap_reg/engine_cap_reg/sw_err_reg/wqcfg, struct grpcfg, DSA EVL structs, IDXD_CMD_* constants.

## Control Flow
Pure hardware-description header consumed by dsa.c to read capabilities, configure workqueues/groups, issue commands, decode software errors, and size descriptor resources.

## State and Persistence
No runtime state; maps MMIO/register layouts into C types.

## Dependencies and Integration Points
Depends on linux/idxd.h and kernel-style bitfield layout assumptions.

## Risks and Edge Cases
Must track hardware spec and kernel driver definitions; bitfield packing is compiler/ABI sensitive.

## Test Signals
Build correctness and successful DSA hardware tests validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/registers.h -->
