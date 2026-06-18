# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.c

## Purpose
`fiji_baco.c` implements BACO state transitions for Fiji-class VI hardware. It is structurally similar to the CI path but uses Fiji register headers, Fiji-specific clock/PLL command tables, and broader BIOS scratch cleanup.

## Important APIs And Control Flow
`fiji_baco_set_state()` reads current state through `smu7_baco_get_state()`, returns early if no transition is needed, then enters BACO by programming GPIOs, frame-buffer request rejection, BCLK bypass, PLL shutdown, clock request switching, and BACO control bits. Exiting waits 20 ms, runs the exit table, and clears BIOS scratch registers 0 through 15 if exit succeeds.

## State, Dependencies, And Integration
Persistent effects are hardware register changes in GPIO, DCE, BIF, GMC, SMU indirect clock controls, MPLL/SPLL, `BACO_CNTL`, and BIOS scratch registers. It depends on `fiji_baco.h`, `smu7_baco.h`, `common_baco.h`, and generated register headers for GMC 8.1, BIF 5.0, DCE 10.0, and SMU 7.1.3.

## Risks And Test Signals
Risks are sequencing drift relative to hardware requirements, ignoring failures before the final enter/exit table, and scratch register cleanup masking firmware assumptions. Test signals are successful BACO in/out on Fiji boards, correct `BACO_MODE` transitions, absence of wait timeouts, stable display and memory clocks after exit, and successful subsequent DPM or reset operations.
