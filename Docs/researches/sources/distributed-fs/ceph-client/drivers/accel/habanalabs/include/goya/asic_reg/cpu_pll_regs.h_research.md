<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_pll_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_pll_regs.h

## Purpose
Auto-generated MMIO offset map for Goya CPU PLL control, divider, lock, reset, clock gating, relaxed clock, and frequency monitoring registers.

## Important APIs, Types, And Functions
- `mmCPU_PLL_NR`, `NF`, `OD`, and `NB` name PLL parameter registers.
- `mmCPU_PLL_CFG`, `LOSE_MASK`, `LOCK_INTR`, `LOCK_BYPASS`, `DATA_CHNG`, and `RST` name configuration, lock/loss, update, and reset controls.
- `mmCPU_PLL_DIV_FACTOR_*`, `DIV_FACTOR_CMD_*`, `DIV_SEL_*`, `DIV_EN_*`, and `DIV_FACTOR_BUSY_*` name four divider lanes.
- `mmCPU_PLL_CLK_GATER` and `CLK_RLX_*` control clock gating/relaxation.
- `mmCPU_PLL_REF_*`, `PLL_NOT_STABLE`, and `FREQ_CALC_EN` support reference/frequency stability monitoring.

## Control Flow
There is no executable code. Goya initialization writes divider and PLL selection registers, may reset or update PLL data, and polls lock/busy/stability registers before using dependent CPU clocks.

## State And Persistence Behavior
PLL configuration is volatile device state, but it controls clocking for the runtime until reset or reprogramming. Busy and stability registers reflect hardware-calculated state.

## Dependencies And Integration Points
Integrates with Goya clock setup, boot timing, reset sequencing, power management, and any code that gates or changes CPU-facing clocks. It depends on generated block bases and register accessors in the driver.

## Risks And Edge Cases
PLL programming mistakes can destabilize the embedded CPU or make the device unreachable. Divider updates require respecting busy bits and command sequencing. Lock bypass and loss masks can hide real clock failures if used incorrectly.

## Test Signals
Signals include stable boot after PLL programming, lock interrupt/status behavior, divider busy bits clearing, measured/reference frequency checks, and absence of clock-related hangs under reset and power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_pll_regs.h -->
