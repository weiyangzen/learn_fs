# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/Makefile

Purpose: Builds the Nuvoton MA35D1 clock controller implementation when `CONFIG_CLK_MA35D1` is enabled.

Important APIs, types, and functions: Adds `clk-ma35d1.o`, `clk-ma35d1-divider.o`, and `clk-ma35d1-pll.o` to `obj-$(CONFIG_CLK_MA35D1)`.

Control flow: Kbuild links the main platform driver, custom ADC divider helper, and custom PLL helper together under the same config symbol.

State and persistence: No runtime state; build composition only.

Dependencies and integration points: Must stay aligned with declarations in `clk-ma35d1.h` and calls from `clk-ma35d1.c`.

Risks: Omitting one helper object would create unresolved symbols for `ma35d1_reg_adc_clkdiv()` or `ma35d1_reg_clk_pll()`. Adding new MA35D1 helper files requires updating this Makefile.

Test signals: Build `CONFIG_CLK_MA35D1=y` with `W=1` and `COMPILE_TEST` to ensure all three objects compile and link.
