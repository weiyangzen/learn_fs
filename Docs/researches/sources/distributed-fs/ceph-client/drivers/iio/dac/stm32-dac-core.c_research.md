## sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac-core.c

Purpose: Parent platform driver for STM32 DAC blocks. It owns shared MMIO regmap, peripheral clock, vref regulator, reset, runtime PM, H7 high-frequency selection, and child device population.

Important APIs/types/functions: `struct stm32_dac_priv` wraps `pclk`, `vref`, and shared `struct stm32_dac_common`. `struct stm32_dac_cfg` marks H7 HFSEL support. `stm32_dac_core_hw_start/stop()` enable/disable regulator and clock. `stm32_dac_probe()` initializes resources and populates children. PM callbacks handle runtime and system suspend/resume.

Control flow: Probe allocates common state, maps MMIO, creates an MMIO regmap clocked by `pclk`, gets clock and vref, enables runtime PM, starts hardware, reads vref mV into common state, optionally toggles reset, sets H7 HFSEL if pclk exceeds 80 MHz, populates child OF nodes, and autosuspends. Remove depopulates children and stops hardware.

State and persistence: Shared `regmap`, `vref_mv`, and `hfsel` persist in `stm32_dac_common` for child channel drivers. Runtime PM may shut down clock/regulator; system resume restores HFSEL if it may have been lost.

Dependencies and integration points: Uses platform resources, `devm_regmap_init_mmio_clk`, regulator, clock, reset controller, OF child population, runtime PM, and the local `stm32-dac-core.h` contract consumed by `stm32-dac.c`.

Risks and test signals: Validate PM reference balancing, child populate/depopulate ordering, HFSEL restore after low-power states, reset handling, and vref capture before children use scale. Tests should cover F4 and H7 compatibles, pclk below/above 80 MHz, runtime suspend/resume, and child probe with parent autosuspended.
