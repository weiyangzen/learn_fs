# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_xtalk.c

## Purpose
Programs the AU88x0 crosstalk cancellation block used by A3D output. It contains coefficient tables for pipe, wide, narrow, and Diamond speaker modes, and writes EQ/XT filters, gains, delays, delay lines, state, sample rate, and enable bits.

## Important APIs, Types, And Functions
Static data includes mode-specific coefficient/gain/delay constants. Hardware writers include `vortex_XtalkHw_SetLeftEQ`, `vortex_XtalkHw_SetRightEQ`, `vortex_XtalkHw_SetLeftXT`, `vortex_XtalkHw_SetRightXT`, state setters, `vortex_XtalkHw_SetGains`, `vortex_XtalkHw_SetDelay`, delay-line setters, `vortex_XtalkHw_SetSampleRate`, `vortex_XtalkHw_Enable`, `vortex_XtalkHw_Disable`, `vortex_XtalkHw_ZeroIO`, `vortex_XtalkHw_ZeroState`, and mode program functions `vortex_XtalkHw_ProgramPipe`, `vortex_XtalkHw_ProgramXtalkWide`, `vortex_XtalkHw_ProgramXtalkNarrow`, `vortex_XtalkHw_ProgramDiamondXtalk`, plus `vortex_XtalkHw_init`.

## Control Flow
A3D initialization calls `vortex_XtalkHw_init()`, `vortex_XtalkHw_SetGainsAllChan()`, a mode-specific programming helper based on `v->xt_mode`, `vortex_XtalkHw_SetSampleRate()`, and `vortex_XtalkHw_Enable()`. A3D shutdown disables the block. Hardware programming is direct MMIO writes over dense coefficient arrays and fixed register offsets.

## State And Persistence
All coefficient tables are static constants. Runtime XTALK state is only in hardware registers and `vortex->xt_mode`; it is zeroed and reprogrammed on A3D initialization. No user persistence exists.

## Dependencies And Integration Points
Depends on `au88x0_xtalk.h`, `au88x0.h`, and MMIO helpers. Integrated through `au88x0_a3d.c`, where XTALK output is routed to playback mixers.

## Risks
The file is dominated by magic coefficients and offsets; audio correctness depends on undocumented hardware behavior. Some right-channel constants exist but are unused, and right XT programming often reuses left-XT data. `vortex_XtalkHw_ZeroState()` writes delay lines twice. Readback helpers are disabled, making runtime verification harder.

## Test Signals
A3D playback through XTALK should be audible in pipe/headphone mode and should change spatial character in speaker/diamond modes. Dmesg should remain clean during A3D enable/disable. A hardware register trace or audible test can validate sample-rate and delay programming.
