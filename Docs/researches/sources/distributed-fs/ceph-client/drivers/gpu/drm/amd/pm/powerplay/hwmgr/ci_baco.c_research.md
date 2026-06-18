# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c

## Purpose
`ci_baco.c` implements BACO enter/exit sequencing for CI-generation SMU7 hardware. It provides `ci_baco_set_state()`, which drives hardware into or out of BACO using static register command tables executed by `baco_program_registers()`.

## Important APIs And Control Flow
The command tables prepare GPIOs, enable frame-buffer request rejection, switch clocks to bypass/reference sources, power down PLLs and memory clocks, assert BACO control bits, wait for BACO mode, and later reverse isolation/power/reset bits. `ci_baco_set_state()` first calls `smu7_baco_get_state()`, returns early if already in the requested state, executes the enter sequence for `BACO_STATE_IN`, and for `BACO_STATE_OUT` waits at least 20 ms before running the exit and cleanup tables.

## State, Dependencies, And Integration
Persistent state is hardware register state: GPIO masks, SMC indirect clock registers, PLL and memory-controller registers, `BACO_CNTL`, BIOS scratch registers, and CP PFP ucode address cleanup. The file depends on `amdgpu.h`, `ci_baco.h`, SMU7 BACO declarations, and CI register definition headers for GMC, BIF, DCE, SMU, and GFX.

## Risks And Test Signals
Risks include wrong magic register values, wait-mask/value mismatches, ignored failures from preparatory tables, and hardware hangs if clock or PLL steps are skipped. Test signals are successful `get_asic_baco_state`/`set_asic_baco_state`, correct BACO mode bits, no timeout in command waits, clean resume from BACO, and no display, memory, or CP firmware corruption after exit.
