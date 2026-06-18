<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.h

## Purpose

This header is the public SMU v14.0.2 PPT hook declaration. It exposes `smu_v14_0_2_set_ppt_funcs(struct smu_context *smu)` so the AMDGPU SMU device selection path can install the v14.0.2-specific `pptable_funcs`, message map, feature map, table map, power-source map, workload map, driver interface version, and mailbox configuration implemented in `smu_v14_0_2_ppt.c`.

## Important APIs, Types, And Control Flow

The only API is the `extern` setter. The header intentionally does not include implementation details or local table types; it relies on users already seeing `struct smu_context` from the surrounding SWSMU headers. Control flow is one-way: ASIC discovery or SMU initialization includes this header, calls the setter for IP 14.0.2, and then uses the function pointers stored in the SMU context.

## State, Dependencies, And Integration

The header has no storage or persistence. Its include guard, `__SMU_V14_0_2_PPT_H__`, prevents duplicate declarations. It is coupled to the C implementation and to the global SWSMU initialization contract that each ASIC PPT module exports a `*_set_ppt_funcs()` symbol.

## Risks And Test Signals

The main risk is declaration drift: if the C implementation changes the function signature or symbol name, the IP selection path will fail at compile or link time. Build coverage for the AMDGPU SWSMU smu14 objects is the primary test signal; runtime coverage is any successful initialization that reaches the v14.0.2 setter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.h -->
