# sources/distributed-fs/ceph-client/drivers/clk/meson/g12a-aoclk.c

## Purpose
`g12a-aoclk.c` describes the Amlogic G12A always-on clock controller. It registers AO peripheral gates, 32 kHz oscillator-derived clocks, CEC clocks, RTC oscillator selection, AO clk81 selection, SAR ADC clocking, and AO reset lines for `amlogic,meson-g12a-aoclkc`.

## Important APIs, Types, And Functions
The file uses `MESON_PCLK()` through `G12A_AO_PCLK()` to define AO gates, `meson_clk_dualdiv_ops` for 32 kHz RTC/CEC dividers, regmap mux/divider/gate ops for AO clock paths, and `struct meson_aoclk_data` to combine clock and reset-controller data. `g12a_ao_reset[]` maps reset IDs to AO reset bits. `g12a_ao_hw_clks[]` maps clock binding IDs. The platform driver probes through `meson_aoclkc_probe()`.

## Control Flow
Probe is handled by the shared AO clock controller code, using `g12a_ao_clkc_data` to register clocks and resets. Runtime operations are generic common-clock callbacks: gate toggles, mux selection, divider programming, and dual-divider table selection. The reset controller uses `AO_RTI_GEN_CNTL_REG0` and the reset bit map supplied in the data structure.

## State, Persistence, And Dependencies
Persistent state lives in AO registers such as `AO_CLK_GATE0`, `AO_CLK_GATE0_SP`, `AO_RTI_PWR_CNTL_REG0`, `AO_RTC_ALT_CLK_CNTL*`, `AO_CEC_CLK_CNTL_REG*`, `AO_SAR_CLK`, and `AO_RTI_GEN_CNTL_REG0`. Dependencies include `meson-aoclk.h`, `clk-regmap.h`, `clk-dualdiv.h`, syscon/regmap access through the parent node, reset-controller support, and G12A AO clock/reset dt-bindings.

## Integration Points
AO peripherals such as IR, I2C, UART, SAR ADC, mailbox, RTI, M3/M4, RTC, and CEC consume these clocks. Many AO gates are marked `CLK_IGNORE_UNUSED` for historical compatibility, with comments encouraging future replacement by narrower flags where possible. The `g12a_ao_clk81` global name is retained for legacy PWM binding behavior.

## Risks And Edge Cases
The file intentionally keeps many AO gates from being disabled, which can hide missing consumers and wastes power, but removing the flag risks regressions. The 32 kHz and CEC clocks depend on the dual-divider table matching the oscillator rate. Reset bit mappings must stay aligned with `dt-bindings/reset/g12a-aoclkc.h`. Legacy global-name use by PWM constrains cleanup.

## Test Signals
Probe tests for `amlogic,meson-g12a-aoclkc`, reset-controller assertions/deassertions, RTC/CEC 32 kHz rate checks, SAR ADC rate programming, suspend/resume tests, and boot tests without unexpected AO gate disabling are useful signals.
