# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100-r.c

## Purpose
`ccu-sun50i-a100-r.c` is the PRCM/R-domain CCU provider for Allwinner A100. It describes the low-power CPU/R bus clocks, APB1/APB2 clocks, peripheral gates for timer, TWD, PWM, PPU, UART, I2C, IR, RTC bus, and their reset controls.

## Important APIs, Types, And Functions
The driver uses `struct ccu_div`, fixed-factor clocks, gate/mux/MP macros, and sunxi-ng descriptor data:

- `r_cpus_clk` is a divider/mux with variable predivider support for parent index 3 (`pll-periph0`), using parents `dcxo24M`, `osc32k`, `iosc`, and `pll-periph0`.
- `r-ahb` is a fixed-factor child of `cpus`.
- `r_apb1_clk` divides `r-ahb`; `r_apb2_clk` uses the same parent set and variable predivider pattern as `cpus`.
- Gate descriptors cover APB1 timer/TWD/PWM bus/PPU/IR bus/RTC and APB2 UART/I2C0/I2C1.
- `r_apb1_pwm_clk` is a mux; `r_apb1_ir_rx_clk` is an MP mux gate.
- `sun50i_a100_r_ccu_resets[]` maps reset IDs to APB/RTC reset bits.
- `sun50i_a100_r_ccu_probe()` maps MMIO and delegates to `devm_sunxi_ccu_probe()`.

## Control Flow
The platform driver matches `allwinner,sun50i-a100-r-ccu`. Probe maps resource 0 and registers clocks/resets through the shared sunxi-ng descriptor path. Runtime operations are generic CCF and reset-controller operations.

Because no custom probe-time register normalization exists, hardware state is taken as firmware left it until consumers request changes.

## State And Persistence
Runtime state is in PRCM registers: CPUS/APB parent selections, divider values, PWM/IR muxes, gate bits, and reset bits. The fixed `r-ahb` clock has no MMIO state of its own; it reflects `cpus`.

There is no cross-boot persistence. Low-power domain state may survive some sleep states depending on hardware and firmware policy, so suspend/resume validation matters.

## Dependencies And Integration Points
The file depends on sunxi-ng common, reset, divider, gate, MP, and NM-related headers plus A100 R binding IDs from `ccu-sun50i-a100-r.h`. It integrates with the A100 PRCM device-tree node, R/low-power timer and watchdog-related blocks, PWM, PPU, UART, I2C, IR receiver, RTC bus, and reset-controller consumers.

Parent clock names such as `dcxo24M`, `osc32k`, `iosc`, and `pll-periph0` must exist in the clock tree.

## Risks
Variable predivider modeling is the main subtlety: `pll-periph0` parent selection requires an extra predivide field. Incorrect handling can produce wrong CPUS/APB2 rates while the clock still appears enabled. Reset bits and gate bits share offsets but use different bit positions, creating the usual risk of mixing enable and reset semantics.

Low-power paths depend on these clocks, so regressions may only appear during suspend/resume, wake, or RTC access rather than during normal boot.

## Test Signals
Successful `sun50i-a100-r-ccu` probe, expected R-domain clocks in `clk_summary`, and reset-controller registration are baseline signals. Hardware tests should cover R timer/TWD, PWM if present, UART/I2C in the R domain, IR receiver, RTC bus access, reset toggles, and suspend/resume wake behavior.
