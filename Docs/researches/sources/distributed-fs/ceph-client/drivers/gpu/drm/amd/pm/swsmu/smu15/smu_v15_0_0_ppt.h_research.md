<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.h

## Purpose

This header declares the SMU v15.0.0 PPT installation function, `smu_v15_0_0_set_ppt_funcs(struct smu_context *smu)`. It is the public handoff between ASIC/IP selection code and the IP 15.0.0-specific implementation in `smu_v15_0_0_ppt.c`.

## Important APIs, Types, And Control Flow

The only symbol is the setter. Callers pass a populated `struct smu_context`; the implementation installs the v15.0.0 `pptable_funcs`, feature map, table map, marks the SMU as APU, records `SMU15_DRIVER_IF_VERSION_SMU_V15_0`, and configures MP1 mailbox registers. The header itself has no direct dependency on the table or PMFW types used by the implementation.

## State, Dependencies, And Integration

The header owns no state. The include guard `__SMU_V15_0_0_PPT_H__` prevents redeclaration. It depends on the broader SWSMU convention that each PPT implementation exposes one setter used by runtime ASIC dispatch and by build-time linkage from the smu15 Makefile.

## Risks And Test Signals

The risk surface is declaration/linkage drift. A mismatch between this header, the C file, and callers will show up as compile or link failures. Runtime test signals are successful IP 15.0.0 SMU initialization and evidence that the v15.0.0 function table, feature map, table map, and mailbox registers were selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.h -->
