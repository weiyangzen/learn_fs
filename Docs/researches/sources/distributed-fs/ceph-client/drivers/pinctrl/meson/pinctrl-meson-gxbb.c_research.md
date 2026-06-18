# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-gxbb.c

Purpose: Provides the legacy Meson GXBB pinctrl data for peripheral and AO domains. Unlike AXG-generation files, GXBB uses the older Meson8 pinmux model from `pinctrl-meson8-pmx.h`, where groups encode mux register/bit data for enable-style muxing rather than per-pin 4-bit selectors.

Important APIs and types: Main objects are `meson_gxbb_periphs_pinctrl_data` and `meson_gxbb_aobus_pinctrl_data`, both using `meson8_pmx_ops`. The file defines pin arrays, `struct meson_pmx_group` arrays using Meson8-style group macros, function maps, and GPIO `struct meson_bank` arrays built with `BANK()`. The AO data uses `meson8_aobus_parse_dt_extra`.

Control flow: `meson_gxbb_pinctrl_driver` matches `amlogic,meson-gxbb-periphs-pinctrl` or `amlogic,meson-gxbb-aobus-pinctrl` and calls the common probe. Runtime mux selection is handled by `meson8_pmx_ops`, using each group data's register/bit information to enable the desired peripheral group. GPIO and pin config operations are still handled by the shared Meson pinctrl core. AO probing invokes the common Meson8 AO parse helper.

State and persistence: The source file is static data only. Hardware state persists in mux and GPIO registers. Periphs banks X, Y, DV, H, Z, CARD, BOOT, and CLK define pull, direction, output, input, and IRQ ranges without drive-strength descriptors. The AO domain covers GPIOAO_0..GPIOAO_13. Because the legacy mux model can enable overlapping groups through bits, mux exclusivity relies on correct common Meson8 PMX behavior and group data.

Dependencies and integration points: Depends on `dt-bindings/gpio/meson-gxbb-gpio.h`, `pinctrl-meson.h`, and `pinctrl-meson8-pmx.h`. Periphs functions include eMMC/NOR/SPI/SDCard/SDIO/NAND, UART A/B/C, I2C A/B/C, Ethernet, PWM variants, HDMI hotplug/I2C, I2S output, SPDIF output, generated clock, and TSIN A/B. AO functions include AO UARTs, AO I2C and slave I2C, remote input, AO PWM variants, AO I2S output, AO SPDIF output, and AO/EE CEC.

Risks: The old mux model differs from AXG, so accidentally using AXG macros or ops would misinterpret group data. Since group names are DT ABI, changes can break older GXBB board files. Several AO functions share pins, such as AO UART/I2C/PWM/CEC choices; mux conflicts must be handled by board pinctrl states. IRQ ranges and bank bit offsets are fixed hardware descriptions with little runtime validation.

Test signals: Build GXBB pinctrl and boot a GXBB board with both periphs and AO nodes. Validate pinmux for storage, Ethernet, HDMI, I2S/SPDIF, TSIN, UART/I2C/SPI, and AO remote/CEC/PWM functions. Check GPIO direction, input/output, pulls, and IRQs across X/Y/DV/H/Z/CARD/BOOT/CLK/AO banks. Compare debug pinctrl state with board DTS group names to catch DT ABI mismatches.
