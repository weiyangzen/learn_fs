# sources/distributed-fs/ceph-client/drivers/clk/mvebu/orion.c

Purpose: Implements early core-clock providers for legacy Marvell Orion SoCs MV88F5181, MV88F5182, MV88F5281, and MV88F6183. It exposes TCLK, CPU, and a single CPU-to-DDR ratio clock through the shared MVEbu core-clock framework.

Important APIs, types, and functions: Four SoC-specific callback groups decode SAR fields: `mv88f5181_get_tclk_freq()`, `mv88f5181_get_cpu_freq()`, `mv88f5181_get_clk_ratio()`, equivalent 5182 and 5281 functions, and `mv88f6183_*()` callbacks. Each group is packaged in a `struct coreclk_soc_desc` with one `orion_coreclk_ratios` entry named `ddrclk`.

Control flow: Each compatible has a dedicated `CLK_OF_DECLARE()` callback. The callback simply calls `mvebu_coreclk_setup(np, &soc_desc)`, allowing the common MVEbu code to map the SAR register and publish the clocks.

State and persistence: The file maintains no dynamic state of its own. Rates are pure functions of the boot strap register, and the resulting CCF registrations persist for the lifetime of the kernel.

Dependencies and integration points: Depends on `drivers/clk/mvebu/common.h`, Linux OF clock early init, and the device-tree compatible string for the core-clock node. Clock consumers depend on the common MVEbu provider naming for CPU, TCLK, and `ddrclk`.

Risks: Unsupported or reserved SAR encodings return zero rates or ratio multiplier zero, which can surface as unusable child clocks. The callback `id` is ignored because there is only one ratio; expanding ratios without adjusting switch logic would be error-prone. These old SoCs have subtly different SAR layouts, so accidental compatible reuse would produce wrong rates.

Test signals: Boot each compatible with known strap values and verify `clk_summary` CPU/TCLK/DDR rates. Invalid strap emulation should produce zero-rate behavior in a controlled way. DT should bind exactly one Orion compatible and no clock-gating behavior is expected from this file.
