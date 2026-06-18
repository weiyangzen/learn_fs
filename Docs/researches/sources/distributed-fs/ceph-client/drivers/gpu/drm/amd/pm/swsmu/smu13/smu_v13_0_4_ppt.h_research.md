# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_4_ppt.h

## Purpose
`smu_v13_0_4_ppt.h` is the public header for the SMU v13.0.4 PPT implementation. It exposes the registration function used by ASIC initialization code.

## Important API
The only API is `smu_v13_0_4_set_ppt_funcs(struct smu_context *smu)`. The implementation assigns APU-specific PPT functions, feature/table maps, driver interface version, APU flag, and mailbox mapping.

## Control Flow
Generic AMDGPU power-management code includes this header, calls the registration function for matching MP1 IP versions, and then interacts with the implementation through `smu->ppt_funcs`.

## State And Persistence
The header owns no state. The implementation mutates the supplied `smu_context`; runtime allocations are handled by its `init_smc_tables` and `fini_smc_tables`.

## Dependencies And Integration Points
It depends on `struct smu_context` from the AMDGPU SMU framework and couples ASIC selection logic to the v13.0.4 PPT implementation.

## Risks
A registration mismatch can install the wrong PMFW maps and make later generic SMU calls send invalid messages. The header itself cannot protect against semantic IP-version mismatches.

## Test Signals
Build coverage and probe coverage are key. v13.0.4/v13.0.11 devices should call this function, set `smu->is_apu`, install non-null PPT functions, and complete SMU DPM initialization.
