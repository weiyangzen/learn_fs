# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xxd.h

## Purpose
`rv6xxd.h` is the RV6xx register-definition header for power management, memory-controller timing, display-gap, thermal, spread-spectrum, and PCIe indirect registers used by `rv6xx_dpm.c`.

## Important APIs, Types, and Functions
The file contains macros only. Important register groups include `SPLL_CNTL_MODE`, `GENERAL_PWRMGT`, `MCLK_PWRMGT_CNTL`, `MPLL_FREQ_LEVEL_0`, `VID_RT`, `TARGET_AND_CURRENT_PROFILE_INDEX`, `VID_UPPER_GPIO_CNTL`, `CG_DISPLAY_GAP_CNTL`, `CG_THERMAL_CTRL`, `CG_SPLL_SPREAD_SPECTRUM_LOW`, `CG_MPLL_SPREAD_SPECTRUM`, memory-controller registers such as `RAMCFG`, `SQM_RATIO`, `ARB_RFSH_RATE`, and PCIe indirect registers `PCIE_P_CNTL`, `PCIE_LC_CNTL`, and `PCIE_LC_SPEED_CNTL`.

## Control Flow
These macros parameterize register writes and bitfield extraction throughout RV6xx DPM. The DPM code reads current profile bits from `TARGET_AND_CURRENT_PROFILE_INDEX`, writes `GENERAL_PWRMGT` to enable voltage/backbias/spread-spectrum/thermal/PCIe control, programs per-level MCLK fields under `MPLL_FREQ_LEVEL_0`, and updates memory refresh and display-gap registers during state transitions.

## State and Persistence
The header itself has no state, but its definitions represent persistent GPU MMIO state. Values written through these macros remain in hardware until subsequent driver writes, GPU reset, or power-state transitions. The current-profile register is also used as the live source for debugfs and current-clock helpers.

## Dependencies and Integration Points
`rv6xxd.h` is integrated with the radeon MMIO accessor macros `RREG32`, `WREG32`, `WREG32_P`, `RREG32_PCIE`, and `RREG32_PCIE_PORT`. It aligns RV6xx bit definitions with `rv6xx_dpm.c` and common `r600_dpm` helpers.

## Risks
Incorrect masks or shifts in this file can silently corrupt hardware programming. Shared macro names such as `SSEN`, `CLKS`, and `CLKV` overlap conceptually with RV730/RV740/RV770 headers but have different field positions, so including the wrong register header for a chip path would produce invalid writes.

## Test Signals
Signals are indirect: DPM enable should set expected `GENERAL_PWRMGT` bits, current-level debugfs should decode profile indices correctly, memory-refresh programming should remain stable across clock changes, and PCIe/thermal/display-gap features should respond without hangs or link-training failures.
