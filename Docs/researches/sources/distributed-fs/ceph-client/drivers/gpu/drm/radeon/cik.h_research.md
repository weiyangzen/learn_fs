# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik.h

## Purpose
`cik.h` is a small private CIK-family Radeon driver interface header. It forward-declares `struct radeon_device` and exposes cross-file entry points for CIK RLC safe mode, memory-controller firmware loading, clock-gating updates, soft-reset probing, command-submission buffer setup, and SDMA lifecycle control.

## Important APIs, types, and dependencies
- Depends on external Radeon core definitions for `struct radeon_device`, `u32`, and `bool`; this file deliberately avoids including the larger driver headers.
- RLC and command-submission APIs: `cik_enter_rlc_safe_mode`, `cik_exit_rlc_safe_mode`, `cik_init_cp_pg_table`, `cik_get_csb_size`, and `cik_get_csb_buffer`.
- Firmware and reset APIs: `ci_mc_load_microcode` and `cik_gpu_check_soft_reset`.
- Power/clock API: `cik_update_cg`.
- SDMA APIs implemented in `cik_sdma.c`: `cik_sdma_resume`, `cik_sdma_enable`, and `cik_sdma_fini`.

## Control flow and integration points
This header is not executable logic; it is an internal contract consumed by CIK ASIC setup, reset, power-management, command-processor, and SDMA code. Callers use these prototypes during device initialization/resume, clock-gating transitions, GPU reset detection, and teardown.

## State and persistence behavior
The file owns no state. The declared functions mutate persistent hardware and driver state through `struct radeon_device`, including RLC mode, microcode-resident controller state, clock-gating registers, command-submission buffers, and SDMA rings.

## Risks and test signals
Prototype drift is the main risk: mismatched definitions or missing declarations break C builds across the Radeon CIK implementation. Runtime validation comes indirectly from CIK device probe/resume, soft-reset paths, SDMA ring/IB tests, command submission, suspend/resume, and clock-gating smoke tests.
