# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg.c

Purpose: Supplies the Amlogic Meson AXG SoC pin controller data for both the peripheral domain and always-on AO bus domain. It defines pin descriptors, mux groups, functions, GPIO bank register maps, AXG 4-bit mux-bank maps, and DT matches for `amlogic,meson-axg-periphs-pinctrl` and `amlogic,meson-axg-aobus-pinctrl`.

Important APIs and types: The important data objects are `meson_axg_periphs_pinctrl_data` and `meson_axg_aobus_pinctrl_data`. They point at separate pin arrays, group arrays, function arrays, GPIO banks, and `meson_axg_pmx_data` structures. The file uses AXG PMX macros (`GROUP`, `GPIO_GROUP`, `BANK_PMX`) and common Meson macros (`MESON_PIN`, `FUNCTION`, `BANK`). Both domains use `meson_axg_pmx_ops`; the AO domain also uses `meson8_aobus_parse_dt_extra`.

Control flow: Platform probing is shared for both compatible strings. The matched `.data` selects either the periphs or AO table. The common core registers the domain, then pinmux requests call the AXG ops to write 4-bit selectors per pin. GPIO requests clear mux selectors to 0. The AO domain parse hook adapts always-on register-map layout before common registration completes.

State and persistence: Static tables are immutable. Runtime mux/GPIO state persists in hardware registers. The periphs domain covers GPIOZ, BOOT, GPIOA, GPIOX, and GPIOY banks with GPIO control registers but no drive-strength descriptors. The AO domain covers GPIOAO pins and GPIO_TEST_N through a separate AO bank. Mux state is split across per-domain `meson_pmx_bank` arrays.

Dependencies and integration points: Depends on `dt-bindings/gpio/meson-axg-gpio.h`, the common Meson pinctrl core, and AXG PMX helper. Peripheral functions include eMMC/NAND/NOR/SDIO, SPI0/1, UART A/B and an AO UART routed on Z pins, I2C0-3, Ethernet, PWM, SPDIF, JTAG, PDM, MCLK, TDM A/B/C, and a generated clock. AO functions include AO UARTs, AO I2C and slave I2C, remote input/output, AO PWMs, AO JTAG, and generated clock. These names are consumed directly by AXG board DT pinctrl states.

Risks: Because AXG has two logical pinctrl domains, periphs/AO compatible selection and parse hooks must match the DT register layout. Using the wrong domain data would make legal pins missing or write the wrong regmap. Function overlap on BOOT/A/X/Y pins is dense; wrong function numbers in `GROUP()` can break storage, Ethernet, or audio with no compile-time warning. AO GPIO_TEST_N inclusion is easy to overlook in IRQ and bank range validation.

Test signals: Boot an AXG board with both periphs and AO pinctrl nodes. Validate pinctrl function enumeration, GPIO mode, pull/direction/output/input, and muxing for storage, SPI, UART, I2C, Ethernet, PWM, audio, and AO remote/PWM/UART functions. Confirm AO parse behavior by checking AO pulls and GPIO operations, not just mux writes.
