# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.c

## Purpose
`polaris_baco.c` implements BACO enter/exit sequencing for Polaris and VegaM SMU7-family hardware. It is table-driven like the CI and Fiji paths but contains alternate BCLK and PLL shutdown sequences for `CHIP_VEGAM`.

## Important APIs And Control Flow
`polaris_baco_set_state()` checks current BACO state through `smu7_baco_get_state()`. Entering BACO programs GPIOs, frame-buffer request rejection, either standard Polaris or VegaM-specific clock bypass and PLL tables, common clock-request table, then BACO control bits. Exiting waits 20 ms, runs exit control sequencing, and clears BIOS scratch 6 and 7 on success.

## State, Dependencies, And Integration
The persistent effects are MMIO state in GPIO, DCE 11, BIF 5, GMC 8.1, SMU 7.1.3 indirect clock registers, MPLL/DRAM controls, `BACO_CNTL`, and BIOS scratch registers. The file depends on `polaris_baco.h`, `common_baco.h`, `smu7_baco.h`, `amdgpu.h`, and generated register headers. It integrates with `pp_get_asic_baco_*` and `pp_set_asic_baco_state()` through hwmgr callback wiring.

## Risks And Test Signals
Risks include using the wrong path for VegaM versus Polaris, ignored failures in preparatory tables, hard-coded undocumented registers, and waits with very short timeouts in PLL shutdown. Test signals are correct BACO mode changes on Polaris10/11/12 and VegaM, no wait failures, clean display/memory recovery after exit, and subsequent DPM/fan/sensor operations working.
