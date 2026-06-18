# sources/distributed-fs/ceph-client/drivers/clk/meson/axg-aoclk.c

Purpose: `axg-aoclk.c` implements the Amlogic AXG always-on clock controller. It provides AO peripheral gates, 32 kHz clock generation/selection, RTC oscillator selection, SARADC clocking, and AO reset mappings.

Important APIs and types: the driver uses `MESON_PCLK`-based gates, `struct clk_regmap` mux/div/gate descriptors, `struct meson_clk_dualdiv_data`, `struct meson_aoclk_data`, and reset binding arrays. The platform driver `axg-ao-clkc` delegates probe to `meson_aoclkc_probe`.

Control flow: AO pclk gates are created from `AO_RTI_GEN_CNTL_REG0` with `CLK_IGNORE_UNUSED`. The 32 kHz path gates `cts_oscin`, enables `axg_ao_32k_pre`, runs a dual-divider table that approximates 32 kHz from xtal, selects between divided and pre clocks, and gates `axg_ao_32k`. RTC oscillator input can select internal 32 kHz or external `ext_32k-0`. SARADC uses mux, divider, and gate descriptors. The `meson_aoclk_data` bundles clock data with reset register and reset line map.

State and persistence: runtime state is in AO register bits and reset bits. AO domain clocks may remain active across low-power states, but the driver stores no persistent data. Registration state is owned by CCF and AO clock helper code.

Dependencies and integration points: it depends on `meson-aoclk`, `clk-regmap`, `clk-dualdiv`, reset controller support, and DT bindings from `axg-aoclkc.h`. Parent firmware names include `mpeg-clk`, `xtal`, and optional external 32 kHz input.

Risks: AO clocks often service wakeup or low-power peripherals; disabling the wrong gate can break remote, UART, I2C, IR, or SARADC behavior. The old PWM binding note on `axg_ao_clk81` means global clock-name compatibility still matters. Reset map indexes must match the reset binding exactly.

Test signals: validate AO consumers for remote, I2C, UART, IR, SARADC, and RTC. Check 32 kHz output accuracy, external 32 kHz selection, reset assert/deassert for AO devices, and suspend/resume wake capability.
