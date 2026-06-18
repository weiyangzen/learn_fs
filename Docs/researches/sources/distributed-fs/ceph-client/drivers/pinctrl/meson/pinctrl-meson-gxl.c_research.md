# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-gxl.c

Purpose: Defines Meson GXL pinctrl data for peripheral and AO domains. It is closely related to GXBB but reflects GXL-specific pin counts, group placements, and functions such as additional I2C placement, Ethernet LED pins, TSIN variants, and smaller AO pin coverage. It uses the legacy Meson8 pinmux engine.

Important APIs and types: The key objects are `meson_gxl_periphs_pinctrl_data` and `meson_gxl_aobus_pinctrl_data`, selected by `meson_gxl_pinctrl_dt_match`. Both use `meson8_pmx_ops`; the AO data uses `meson8_aobus_parse_dt_extra`. Static data includes pin descriptor arrays, Meson8-style group arrays, function arrays, and GPIO bank arrays built with `BANK()`.

Control flow: The platform driver matches `amlogic,meson-gxl-periphs-pinctrl` or `amlogic,meson-gxl-aobus-pinctrl`, then delegates to `meson_pinctrl_probe()`. At runtime, pinctrl state application uses `meson8_pmx_ops` to set the mux bits encoded in each group. GPIO, pull, direction, output, input, and IRQ handling come from the shared Meson core using this file's bank descriptors.

State and persistence: This file stores immutable hardware-description tables. Register state persists in mux and GPIO hardware. Periphs banks are X, DV, H, Z, CARD, BOOT, and CLK. AO bank coverage is GPIOAO_0..GPIOAO_9, unlike GXBB's larger AO range. No drive-strength register descriptors are supplied in these legacy `BANK()` entries.

Dependencies and integration points: Depends on `dt-bindings/gpio/meson-gxl-gpio.h`, `pinctrl-meson.h`, and `pinctrl-meson8-pmx.h`. Periphs functions include eMMC/NOR/SPI/SDCard/SDIO/NAND, UART A/B/C, I2C A/B/C/D, Ethernet and Ethernet LED pins, PWM A-F, HDMI hotplug/I2C, I2S output, SPDIF output, and TSIN A/B with alternate placements. AO functions include AO UARTs, AO I2C and slave I2C, remote input, AO PWM A/B, AO I2S/SPDIF output, and CEC.

Risks: GXL differs from GXBB in bank sizes and group availability despite similar structure; copying board pinctrl data between them can select nonexistent or different pins. AO pin count is smaller, so GXBB AO group assumptions are unsafe. Legacy mux group data must be interpreted by `meson8_pmx_ops`, not AXG ops. Ethernet LED and TSIN alternate groups share pins with other peripherals and need board-level conflict review.

Test signals: Build and boot on GXL hardware using both compatible strings. Verify pinctrl function/group enumeration against DTS, mux storage and network peripherals, HDMI/CEC, I2S/SPDIF, TSIN, UART/I2C/SPI, PWM, Ethernet LEDs, and AO remote/PWM/CEC functions. Test GPIO input/output, pulls, and IRQs across each bank, especially AO and GXL-specific H/Z/X differences.
