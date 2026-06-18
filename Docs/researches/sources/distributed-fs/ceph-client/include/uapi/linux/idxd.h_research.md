<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/idxd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/idxd.h

## Purpose
`idxd.h` defines the userspace descriptor and completion ABI for Intel Data Streaming Accelerator and In-Memory Analytics Accelerator devices exposed through the idxd driver.

## Important APIs, types, and functions
The header defines software command status codes in `enum idxd_scmd_stat`, descriptor flags `IDXD_OP_FLAG_*`, DSA opcodes in `enum dsa_opcode`, IAX opcodes in `enum iax_opcode`, completion status enums for DSA and IAX, status mask helpers, and packed descriptor/completion structures. `struct dsa_hw_desc` encodes PASID/privilege, flags, opcode, completion address, source/destination/pattern/list/translation operands, transfer size or descriptor count, interrupt handle, and operation-specific fields for compare, delta, CRC, DIF/DIX, fill, and translation fetch. `struct iax_hw_desc` encodes compression/analytics operands. Raw descriptor and completion record wrappers expose fixed 64-bit field arrays.

## Control flow
User space configures a work queue through sysfs/driver control, maps or opens a portal, writes a DSA or IAX descriptor, waits for completion record status to change, then decodes result, bytes completed, fault address, invalid flags, CRC/DIF/analytics fields, or page-fault status.

## State and persistence behavior
Descriptor and completion records are shared memory ABI. Completion status is written by hardware and marked volatile. Work queue configuration, PASID, interrupt handle, and device/workqueue enablement are persistent driver/device state outside this header.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with idxd character devices, sysfs workqueue setup, IOMMU/SVA/PASID, DSA/IAX hardware portals, DMA memory, and accelerator libraries.

## Risks and test signals
Risks include packed bitfield layout portability, missing memory barriers around volatile completion status, invalid PASID or privilege, page fault handling, descriptor alignment, overlapping buffers, unsupported opcodes/flags, and IOMMU-disabled user queues. Test signals include DSA/IAX user tests, opcode success/error coverage, page-fault injection, invalid flag reporting, workqueue enable failure codes, completion polling barriers, and descriptor size/static assert checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/idxd.h -->
