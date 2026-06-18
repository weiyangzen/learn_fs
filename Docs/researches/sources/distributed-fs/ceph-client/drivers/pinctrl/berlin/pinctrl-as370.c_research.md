# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/pinctrl-as370.c

Purpose: Synaptics AS370 pinctrl descriptor driver using the Berlin common core with a direct MMIO regmap.

Important APIs/types/functions: `as370_soc_pinctrl_groups` describes AS370 mux groups, mostly audio, PDM, NAND/eMMC, SPI, USB, TWI, JTAG, PWM, UART, and SD0 pins. `as370_pinctrl_probe()` maps resource 0, creates a 32-bit regmap, and delegates to `berlin_pinctrl_probe_regmap()`.

Control flow: platform driver matches `syna,as370-soc-pinctrl`, retrieves descriptor data, initializes regmap-mmio from the pinctrl resource, then registers via the Berlin core.

State and persistence: mux state resides in MMIO registers; file-local state is static descriptor data only.

Dependencies/integration: OF/platform/regmap and Berlin core. Consumers request named functions through DT `function`/`groups` properties.

Risks: AS370 uses several mux values for reset, PLL, and debug outputs; bad pin states can disrupt boot-critical rails or clocks. Regmap `max_register` is set to resource size, so hardware descriptions must expose the correct span.

Test signals: compile with `PINCTRL_AS370`, boot an AS370 DT, validate debugfs group/function membership, and verify representative I2S, NAND/eMMC, and SD0 mux register writes.
