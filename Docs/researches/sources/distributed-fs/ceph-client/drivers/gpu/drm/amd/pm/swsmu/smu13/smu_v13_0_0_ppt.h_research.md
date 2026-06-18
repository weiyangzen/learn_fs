# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.h

## Purpose
`smu_v13_0_0_ppt.h` is the minimal public header for the SMU v13.0.0 PPT implementation. It declares the v13.0.0 registration entry point.

## Important API
The only API is `smu_v13_0_0_set_ppt_funcs(struct smu_context *smu)`. Calling it installs v13.0.0 `pptable_funcs`, mapping tables, driver interface version, and message-control setup into the supplied SMU context.

## Control Flow
ASIC initialization includes this header and calls the registration function for matching hardware. After registration, generic SMU code uses `smu->ppt_funcs` instead of direct v13.0.0 calls.

## State And Persistence
The header owns no state. The declared implementation mutates `struct smu_context`; runtime allocations and persistence behavior live in `smu_v13_0_0_ppt.c`.

## Dependencies And Integration Points
It depends on `struct smu_context` from the AMDGPU SMU framework and couples ASIC selection code to the v13.0.0 implementation.

## Risks
Interface drift is the main risk. If the implementation changes registration side effects or the function name, this header and all callers must be updated together.

## Test Signals
Build coverage and device probe are sufficient: v13.0.0 hardware should call this registration function, receive non-null PPT functions, and complete SMU initialization.
