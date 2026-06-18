# Research Report: subset-b-005063

This grouped report covers the requested Amlogic Meson pinctrl source files under `sources/distributed-fs/ceph-client/drivers/pinctrl/meson`. Each section is delimited for reconciliation into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-c3.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-c3.c

Purpose: Defines the pin controller description for the Amlogic C3 peripheral GPIO domain. The file is almost entirely static SoC data: pin descriptors, alternate-function pin groups, function-to-group maps, GPIO bank register layouts, AXG-style mux bank layouts, the `meson_pinctrl_data` instance, and the platform-driver/device-tree binding for `amlogic,c3-periphs-pinctrl`.

Important APIs and types: The key exported-to-core object is `c3_periphs_pinctrl_data`, which is selected from `c3_pinctrl_dt_match` and consumed by `meson_pinctrl_probe()`. It uses `struct pinctrl_pin_desc`, `struct meson_pmx_group`, `struct meson_pmx_func`, `struct meson_bank`, `struct meson_pmx_bank`, and `struct meson_axg_pmx_data`. The file uses `MESON_PIN()`, `GROUP()`, `GPIO_GROUP()`, `FUNCTION()`, `BANK_DS()`, and `BANK_PMX()` macros from the common Meson pinctrl headers. Its mux implementation is `meson_axg_pmx_ops`, and its DT parser is `meson_a1_parse_dt_extra`.

Control flow: Module load registers `c3_pinctrl_driver`. On a DT match for `amlogic,c3-periphs-pinctrl`, platform probe enters the shared Meson pinctrl core with `.data = &c3_periphs_pinctrl_data`. The core registers pins, pinmux functions, pin configuration, GPIO chip, and register maps. Later pinctrl state application resolves a function name to one or more group names, then `meson_axg_pmx_ops.set_mux` writes the 4-bit mux selector stored in each group. GPIO requests use the AXG mux path to select function value 0.

State and persistence: The source file owns no runtime state; it supplies immutable tables. Runtime state lives in the common `struct meson_pinctrl`, Linux pinctrl/gpio objects, and hardware registers reached through regmaps. Selected mux values, pull enable/pull value, direction, output, input, and drive-strength settings persist in SoC registers until changed by another pinctrl/GPIO consumer or reset. `BANK_DS()` entries expose drive-strength registers for all C3 banks.

Dependencies and integration points: Depends on `dt-bindings/gpio/amlogic-c3-gpio.h`, `pinctrl-meson.h`, and `pinctrl-meson-axg-pmx.h`. The pin names must match DT binding numbers and device-tree pinctrl nodes. Peripheral group coverage includes UART A/B/C/D/E, I2C0-3 and slave I2C, PWM A-N plus high-impedance PWM C, IR, JTAG A/B, general clocks, eMMC/NAND/SPIF/SPI A/B/SDCard/SDIO, PDM, Ethernet LED, audio clocks/TDM, and LCD signals. The GPIO banks are X, D, E, C, B, A, and TEST_N with distinct register windows; the mux banks map those logical banks into AXG 4-bit mux registers.

Risks: This is hardware-description code where most failures are silent misrouting rather than compile errors. Incorrect GPIO numbering, group pin membership, or mux function values can route a peripheral to the wrong pad. Register offsets in `BANK_DS()` and `BANK_PMX()` are especially risky because they control unrelated pins if off by one register or bit group. The many overlapping alternate functions on the same pins make group/function review important when adding C3 board pinctrl states. DT compatibility or binding drift would prevent probe or make board dts files select unavailable groups.

Test signals: Build with the C3 pinctrl driver enabled, boot a C3 DT using `amlogic,c3-periphs-pinctrl`, and check that pinctrl registration shows the expected pins/functions. Runtime validation should exercise GPIO input/output, pull-up/down, drive strength, and muxed peripherals on representative banks: eMMC or SDIO, SPI, UART, I2C, PWM, Ethernet LED, PDM/TDM, LCD, and TEST_N. Useful failure signals include pinctrl group lookup errors, regmap write failures, wrong GPIO IRQ numbering, and peripheral probe failures after pinmux state application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-c3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-t7.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-t7.c

Purpose: Provides the Amlogic T7 peripheral pin controller tables. It describes a large single peripheral GPIO domain with pin descriptors, many alternate-function groups, function maps, GPIO bank register descriptors including drive strength, AXG-style 4-bit mux bank descriptors, and the platform driver for `amlogic,t7-periphs-pinctrl`.

Important APIs and types: `t7_periphs_pinctrl_data` is the central data object passed to `meson_pinctrl_probe()`. It references `t7_periphs_pins`, `t7_periphs_groups`, `t7_periphs_functions`, `t7_periphs_banks`, and `t7_periphs_pmx_banks_data`. The file uses the shared Meson data types (`struct meson_pmx_group`, `struct meson_pmx_func`, `struct meson_bank`, `struct meson_pmx_bank`, `struct meson_axg_pmx_data`) and macro layer (`MESON_PIN`, `GROUP`, `GPIO_GROUP`, `FUNCTION`, `BANK_DS`, `BANK_PMX`). Pinmux operations are delegated to `meson_axg_pmx_ops`, and extra DT parsing uses `meson_a1_parse_dt_extra`.

Control flow: The Linux platform bus matches `amlogic,t7-periphs-pinctrl` in `t7_pinctrl_dt_match`, then calls the common `meson_pinctrl_probe()` through `t7_pinctrl_driver`. The common core registers the T7 pin ranges and functions. At runtime, selecting a pinctrl state finds a function entry such as `spi0`, `i2c5`, `eth`, `vx1_a`, or `edp_b`, enumerates its group names, and asks `meson_axg_pmx_ops` to write the per-group function number into the correct 4-bit mux slot for each pin.

State and persistence: All data in the file is immutable. Runtime state is in the common Meson pinctrl device and in hardware regmaps. Mux selectors, GPIO direction/output/input, pulls, and drive strength persist in T7 GPIO controller registers. `BANK_DS()` is used for banks D, E, Z, H, C, B, X, T, Y, W, M, and TEST_N, giving each bank explicit pull, direction, output, input, and drive-strength register offsets plus IRQ ranges.

Dependencies and integration points: Depends on `dt-bindings/gpio/amlogic,t7-periphs-pinctrl.h`, the shared Meson pinctrl core, and the AXG pinmux helper. It is a binding contract for board/device-tree users that reference T7 pin group names. Covered functions include storage buses (eMMC/NAND, NOR, SDCard, SDIO), six SPI controllers, many UARTs including AO-labeled UARTs, PWM and PWM high-impedance variants, TDM/audio/PDM/SPDIF/MCLK, I2C0-5 and AO I2C, HDMI RX/TX, CEC, remote input/output, watchdog reset, RTC clock, Ethernet, ISO7816, transport stream inputs, PCIe clock request, sync/video, V-by-One, eDP hotplug, and microphone mute. The mux bank table maps banks D/E/Z/H/C/B/X/T/Y/W/M/TEST_N to mux register offsets.

Risks: T7 has a high number of pins and alternate functions, so copy/paste mistakes in pin arrays, group names, or function numbers are the main risk. Since group names are string-based ABI for device tree, renaming or removing a group can break board files. Mux-bank and GPIO-bank register offsets are not type-checked against hardware manuals; an incorrect offset can corrupt another bank. The file mixes AO-named peripheral functions into the periphs domain, so assumptions from older split periphs/AO drivers can be wrong.

Test signals: Compile-test the driver and boot on T7 hardware with a DT node using `amlogic,t7-periphs-pinctrl`. Confirm pinctrl lists all expected functions and groups. Runtime tests should cover at least one group in every mux bank, GPIO IRQ ranges, pull and drive-strength settings, and representative high-value functions: eMMC/SDIO, SPI0-5, I2C buses, UARTs, Ethernet, HDMI/CEC, TS inputs, audio TDM/PDM/SPDIF, PWM including high-impedance groups, PCIe clock request, and display hotplug pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-t7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-a1.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-a1.c

Purpose: Defines the pin controller data for the Amlogic Meson A1 peripheral GPIO banks. It maps A1 pins to GPIO names, peripheral pin groups, pinmux functions, GPIO control banks with drive strength, AXG-generation mux banks, and a platform driver compatible with `amlogic,meson-a1-periphs-pinctrl`.

Important APIs and types: The main object is `meson_a1_periphs_pinctrl_data`, selected by `meson_a1_pinctrl_dt_match` and probed by `meson_pinctrl_probe()`. Static data arrays include `meson_a1_periphs_pins`, `meson_a1_periphs_groups`, `meson_a1_periphs_functions`, `meson_a1_periphs_banks`, `meson_a1_periphs_pmx_banks`, and `meson_a1_periphs_pmx_banks_data`. The file uses `GROUP()` and `GPIO_GROUP()` from the AXG PMX header, so each group carries a 4-bit mux function number in `struct meson_pmx_axg_data`.

Control flow: Driver registration is standard `module_platform_driver()`. When the DT node matches, the common Meson pinctrl probe uses `meson_a1_periphs_pinctrl_data` to register pinctrl and GPIO services. Pinctrl state changes use `meson_axg_pmx_ops`: for each selected group, the AXG helper calculates the register/offset from `meson_a1_periphs_pmx_banks` and writes the group function selector. GPIO requests select function 0 for the pin.

State and persistence: The file contributes immutable metadata only. Hardware-visible state is persistent in GPIO and mux registers until changed or reset. The bank table covers P, B, X, F, and A banks with pull-enable, pull, direction, output, input, and drive-strength registers. Because the data uses `meson_a1_parse_dt_extra`, runtime regmap assignment follows the A1-style common DT parsing path.

Dependencies and integration points: Depends on `dt-bindings/gpio/meson-a1-gpio.h`, `pinctrl-meson.h`, and `pinctrl-meson-axg-pmx.h`. It integrates with storage and low-speed peripheral drivers through DT pinctrl group names. Functions include PSRAM, PWM A-F and high-impedance PWM variants, SPIF, SDCard, TDM A/B and VAD TDM, UART A/B/C, I2C0-3, SPI A, PDM, generated clocks, remote input/output, JTAG A, 32 kHz input, SPDIF input, SWD-like `sw`, 25 MHz clock, CEC A/B, mute key/enable, and test outputs.

Risks: A1 pin groups often provide alternate placements for the same function across banks, so incorrect function numbers can make a legal group select the wrong hardware signal. The PSRAM pins occupy an entire bank and are timing-sensitive. Drive-strength offsets are board-signal-quality relevant; incorrect values may pass simple GPIO testing but fail under high-speed SDCard/SPIF/PSRAM operation. Group names are DT ABI and should not be churned casually.

Test signals: Build and boot with `amlogic,meson-a1-periphs-pinctrl`. Verify pinctrl function/group enumeration, GPIO direction/input/output, GPIO IRQs, pull configuration, and drive-strength writes. Exercise PSRAM, SDCard/SPIF, UART, I2C, SPI, PWM and PWM high-Z modes, TDM/PDM/audio clocks, CEC, remote input/output, and mute pins on actual A1 hardware or board-level loopback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-a1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg-pmx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg-pmx.c

Purpose: Implements the second-generation AXG-style Meson pinmux operations used by Meson AXG and later SoCs in this directory. This hardware model gives each pin a continuous 4-bit function selector; function value 0 selects GPIO mode and nonzero values select peripheral modes.

Important APIs and functions: The exported API is `const struct pinmux_ops meson_axg_pmx_ops`. Important helpers are `meson_axg_pmx_get_bank()`, `meson_pmx_calc_reg_and_offset()`, `meson_axg_pmx_update_function()`, `meson_axg_pmx_set_mux()`, and `meson_axg_pmx_request_gpio()`. The implementation consumes `struct meson_pinctrl`, `struct meson_axg_pmx_data`, `struct meson_pmx_bank`, `struct meson_pmx_group`, and per-group `struct meson_pmx_axg_data`.

Control flow: The common pinctrl core calls `.set_mux` with a function selector and group selector. `meson_axg_pmx_set_mux()` obtains driver data from the `pinctrl_dev`, looks up the selected function and group, reads the AXG function number stored in `group->data`, and iterates every pin in the group. Each pin is passed to `meson_axg_pmx_update_function()`, which locates the enclosing mux bank, calculates the mux register and bit offset, and calls `regmap_update_bits()` on `pc->reg_mux`. GPIO request flow enters `.gpio_request_enable`, which writes function 0 for the requested pin.

State and persistence: The file keeps no private mutable state. It mutates SoC mux registers through `pc->reg_mux`; those writes persist as hardware pinmux state. It relies on immutable SoC-specific `pmx_banks` tables and group data prepared by files such as `pinctrl-meson-axg.c`, `pinctrl-meson-a1.c`, `pinctrl-amlogic-c3.c`, and `pinctrl-amlogic-t7.c`.

Dependencies and integration points: Depends on Linux regmap and pinctrl/pinmux APIs plus the shared Meson pinctrl structures. It integrates with `meson_pmx_get_funcs_count`, `meson_pmx_get_func_name`, and `meson_pmx_get_groups` for common function enumeration. The companion header supplies `BANK_PMX`, `GROUP`, and `GPIO_GROUP` macros that build the data consumed here. `EXPORT_SYMBOL_GPL(meson_axg_pmx_ops)` allows SoC pinctrl modules to reference these operations.

Risks: `meson_axg_pmx_get_bank()` returns `-EINVAL` if a pin is not covered by a mux bank, so SoC data omissions cause runtime mux failures. `meson_pmx_calc_reg_and_offset()` assumes exactly four bits per pin and a linear bank mapping; any SoC with holes or non-4-bit selectors needs different ops or carefully split banks. The write uses `reg << 2`, so table register values are word indexes, not byte offsets; inconsistent units in `BANK_PMX()` tables would write wrong registers. Group data is cast to `struct meson_pmx_axg_data`, so old Meson8-style groups must not be paired with these ops.

Test signals: Unit-style coverage is mostly compile-time plus runtime pinmux operations. Test by selecting mux groups on each bank for AXG/A1/C3/T7/G12A hardware, requesting pins as GPIO after peripheral muxing, and checking `regmap_update_bits()` effects via register dumps. Failure signals include `-EINVAL` on valid groups, wrong mux values for multi-pin groups, GPIO request not clearing peripheral function, or pinctrl state application failures during peripheral probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg-pmx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg-pmx.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg-pmx.h

Purpose: Declares the data structures and macros used by the AXG-generation Meson pinmux implementation. It is the contract between SoC-specific pin table files and `pinctrl-meson-axg-pmx.c`.

Important APIs and types: Defines `struct meson_pmx_bank` with bank name, first/last pin, mux register index, and starting bit offset. Defines `struct meson_axg_pmx_data`, which wraps a mux-bank array and count. Defines `struct meson_pmx_axg_data`, which carries the 4-bit function selector for a group. Macros `BANK_PMX()`, `PMX_DATA()`, `GROUP()`, and `GPIO_GROUP()` build the static objects consumed by `meson_axg_pmx_ops`. The header also declares `extern const struct pinmux_ops meson_axg_pmx_ops`.

Control flow: No executable code is present. The macros expand inside SoC table files to initialize `struct meson_pmx_group` entries and mux-bank data. At runtime the AXG pinmux implementation reads those structures through `pc->data->groups[group_num].data` and `pc->data->pmx_data`.

State and persistence: The header defines immutable table shapes, not runtime state. Its function selector values eventually become persistent hardware mux state when `meson_axg_pmx_ops` writes mux registers.

Dependencies and integration points: It assumes inclusion after common Meson pinctrl definitions and availability of `ARRAY_SIZE`. It is used by AXG-style SoC data files including AXG, G12A, A1, C3, and T7. It intentionally differs from `pinctrl-meson8-pmx.h`, where legacy SoCs use bit-enable mux groups rather than per-pin 4-bit selectors.

Risks: Macro-generated compound literals must remain valid for static initialization patterns used in the SoC files. Any change to `struct meson_pmx_axg_data` or `GROUP()` layout must be synchronized with the cast in `meson_axg_pmx_set_mux()`. Because `BANK_PMX()` table register units are later shifted by `reg << 2`, the unit convention must be documented and preserved. The header lacks include guards in the shown source, so duplicate inclusion in one translation unit would be risky, although current users include it once.

Test signals: Compile all AXG-generation pinctrl drivers. Runtime validation is indirect: successful mux selection for groups created by `GROUP()`, successful GPIO mode for groups created by `GPIO_GROUP()`, and correct mux-bank lookup for every `BANK_PMX()` range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg-pmx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg.c

Purpose: Supplies the Amlogic Meson AXG SoC pin controller data for both the peripheral domain and always-on AO bus domain. It defines pin descriptors, mux groups, functions, GPIO bank register maps, AXG 4-bit mux-bank maps, and DT matches for `amlogic,meson-axg-periphs-pinctrl` and `amlogic,meson-axg-aobus-pinctrl`.

Important APIs and types: The important data objects are `meson_axg_periphs_pinctrl_data` and `meson_axg_aobus_pinctrl_data`. They point at separate pin arrays, group arrays, function arrays, GPIO banks, and `meson_axg_pmx_data` structures. The file uses AXG PMX macros (`GROUP`, `GPIO_GROUP`, `BANK_PMX`) and common Meson macros (`MESON_PIN`, `FUNCTION`, `BANK`). Both domains use `meson_axg_pmx_ops`; the AO domain also uses `meson8_aobus_parse_dt_extra`.

Control flow: Platform probing is shared for both compatible strings. The matched `.data` selects either the periphs or AO table. The common core registers the domain, then pinmux requests call the AXG ops to write 4-bit selectors per pin. GPIO requests clear mux selectors to 0. The AO domain parse hook adapts always-on register-map layout before common registration completes.

State and persistence: Static tables are immutable. Runtime mux/GPIO state persists in hardware registers. The periphs domain covers GPIOZ, BOOT, GPIOA, GPIOX, and GPIOY banks with GPIO control registers but no drive-strength descriptors. The AO domain covers GPIOAO pins and GPIO_TEST_N through a separate AO bank. Mux state is split across per-domain `meson_pmx_bank` arrays.

Dependencies and integration points: Depends on `dt-bindings/gpio/meson-axg-gpio.h`, the common Meson pinctrl core, and AXG PMX helper. Peripheral functions include eMMC/NAND/NOR/SDIO, SPI0/1, UART A/B and an AO UART routed on Z pins, I2C0-3, Ethernet, PWM, SPDIF, JTAG, PDM, MCLK, TDM A/B/C, and a generated clock. AO functions include AO UARTs, AO I2C and slave I2C, remote input/output, AO PWMs, AO JTAG, and generated clock. These names are consumed directly by AXG board DT pinctrl states.

Risks: Because AXG has two logical pinctrl domains, periphs/AO compatible selection and parse hooks must match the DT register layout. Using the wrong domain data would make legal pins missing or write the wrong regmap. Function overlap on BOOT/A/X/Y pins is dense; wrong function numbers in `GROUP()` can break storage, Ethernet, or audio with no compile-time warning. AO GPIO_TEST_N inclusion is easy to overlook in IRQ and bank range validation.

Test signals: Boot an AXG board with both periphs and AO pinctrl nodes. Validate pinctrl function enumeration, GPIO mode, pull/direction/output/input, and muxing for storage, SPI, UART, I2C, Ethernet, PWM, audio, and AO remote/PWM/UART functions. Confirm AO parse behavior by checking AO pulls and GPIO operations, not just mux writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-g12a.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-g12a.c

Purpose: Defines Meson G12A pinctrl data for peripheral and always-on domains. It is an AXG-generation 4-bit mux driver data file with expanded G12A pin coverage, interrupt binding identifiers, drive-strength-aware banks, special AO/GPIOE handling, and platform-driver matches for `amlogic,meson-g12a-periphs-pinctrl` and `amlogic,meson-g12a-aobus-pinctrl`.

Important APIs and types: The central objects are `meson_g12a_periphs_pinctrl_data` and `meson_g12a_aobus_pinctrl_data`. The file uses `struct meson_bank` entries built with `BANK_DS()` and IRQ IDs from `dt-bindings/interrupt-controller/amlogic,meson-g12a-gpio-intc.h`, `struct meson_pmx_bank` entries built with `BANK_PMX()`, and AXG-style `GROUP()` entries. It defines a local `meson_g12a_aobus_parse_dt_extra()` hook that aliases AO pull and pull-enable regmaps to `pc->reg_gpio`.

Control flow: Device-tree matching selects periphs or AO data and runs `meson_pinctrl_probe()`. For peripheral muxing, `meson_axg_pmx_ops` writes mux selectors for Z, H, BOOT, C, A, and X banks. AO muxing uses separate AO and E mux banks. During AO probe, `meson_g12a_aobus_parse_dt_extra()` adjusts regmap pointers before the common core registers pin config support.

State and persistence: Static tables are immutable. Hardware state includes mux selectors, GPIO direction/output/input, pulls, and drive strength. Periphs banks Z/H/BOOT/C/A/X use interrupt IDs from the G12A GPIO interrupt-controller binding. AO banks include GPIOAO_0..GPIOAO_11 and GPIOE_0..GPIOE_2; GPIOE is explicitly noted as physically located in the AO bank and uses offset 16 for pull/dir/out/in control fields.

Dependencies and integration points: Depends on `dt-bindings/gpio/meson-g12a-gpio.h`, G12A GPIO interrupt-controller dt-bindings, common Meson pinctrl, and AXG PMX. Peripheral functions include storage (eMMC/NAND/NOR/SDIO/SDCard), SPI0/1, I2C0-3, UART A/B/C and AO UART routed on H/C, ISO7816, Ethernet, PWM A-F, CEC on H pins, JTAG, BT565, TS inputs, HDMI TX, PDM, SPDIF, MCLK/TDM audio, and PCIe clock request. AO functions include AO UART/I2C, remote input/output, AO PWMs, JTAG A, CEC, TSIN AO, SPDIF AO, TDM AO, and MCLK AO.

Risks: G12A combines periphs, AO, and GPIOE special placement, making register-map setup more subtle than single-domain files. IRQ ID definitions must match the interrupt-controller binding, or GPIO IRQ consumers receive wrong hwirqs. `meson_g12a_aobus_parse_dt_extra()` changes pull regmaps to the GPIO regmap; omitting it would break AO pulls. Dense alternate functions and multiple placements for SDCard, SPI, UART, CEC, and audio functions increase risk of group/function mismatch.

Test signals: Build and boot on G12A-family hardware with both compatible strings. Check GPIO IRQ mapping against the interrupt controller, pin config for pulls and drive strength, AO GPIOE operations, and muxing for eMMC/SDIO/SDCard, SPI, I2C, UART, Ethernet, HDMI/CEC, TSIN, PDM/SPDIF/TDM/MCLK, PCIe clock request, and AO remote/PWM/CEC functions. Register dumps should confirm AO pull bits live in the GPIO regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-g12a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-gxbb.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-gxbb.c

Purpose: Provides the legacy Meson GXBB pinctrl data for peripheral and AO domains. Unlike AXG-generation files, GXBB uses the older Meson8 pinmux model from `pinctrl-meson8-pmx.h`, where groups encode mux register/bit data for enable-style muxing rather than per-pin 4-bit selectors.

Important APIs and types: Main objects are `meson_gxbb_periphs_pinctrl_data` and `meson_gxbb_aobus_pinctrl_data`, both using `meson8_pmx_ops`. The file defines pin arrays, `struct meson_pmx_group` arrays using Meson8-style group macros, function maps, and GPIO `struct meson_bank` arrays built with `BANK()`. The AO data uses `meson8_aobus_parse_dt_extra`.

Control flow: `meson_gxbb_pinctrl_driver` matches `amlogic,meson-gxbb-periphs-pinctrl` or `amlogic,meson-gxbb-aobus-pinctrl` and calls the common probe. Runtime mux selection is handled by `meson8_pmx_ops`, using each group data's register/bit information to enable the desired peripheral group. GPIO and pin config operations are still handled by the shared Meson pinctrl core. AO probing invokes the common Meson8 AO parse helper.

State and persistence: The source file is static data only. Hardware state persists in mux and GPIO registers. Periphs banks X, Y, DV, H, Z, CARD, BOOT, and CLK define pull, direction, output, input, and IRQ ranges without drive-strength descriptors. The AO domain covers GPIOAO_0..GPIOAO_13. Because the legacy mux model can enable overlapping groups through bits, mux exclusivity relies on correct common Meson8 PMX behavior and group data.

Dependencies and integration points: Depends on `dt-bindings/gpio/meson-gxbb-gpio.h`, `pinctrl-meson.h`, and `pinctrl-meson8-pmx.h`. Periphs functions include eMMC/NOR/SPI/SDCard/SDIO/NAND, UART A/B/C, I2C A/B/C, Ethernet, PWM variants, HDMI hotplug/I2C, I2S output, SPDIF output, generated clock, and TSIN A/B. AO functions include AO UARTs, AO I2C and slave I2C, remote input, AO PWM variants, AO I2S output, AO SPDIF output, and AO/EE CEC.

Risks: The old mux model differs from AXG, so accidentally using AXG macros or ops would misinterpret group data. Since group names are DT ABI, changes can break older GXBB board files. Several AO functions share pins, such as AO UART/I2C/PWM/CEC choices; mux conflicts must be handled by board pinctrl states. IRQ ranges and bank bit offsets are fixed hardware descriptions with little runtime validation.

Test signals: Build GXBB pinctrl and boot a GXBB board with both periphs and AO nodes. Validate pinmux for storage, Ethernet, HDMI, I2S/SPDIF, TSIN, UART/I2C/SPI, and AO remote/CEC/PWM functions. Check GPIO direction, input/output, pulls, and IRQs across X/Y/DV/H/Z/CARD/BOOT/CLK/AO banks. Compare debug pinctrl state with board DTS group names to catch DT ABI mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-gxbb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-gxl.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-gxl.c

Purpose: Defines Meson GXL pinctrl data for peripheral and AO domains. It is closely related to GXBB but reflects GXL-specific pin counts, group placements, and functions such as additional I2C placement, Ethernet LED pins, TSIN variants, and smaller AO pin coverage. It uses the legacy Meson8 pinmux engine.

Important APIs and types: The key objects are `meson_gxl_periphs_pinctrl_data` and `meson_gxl_aobus_pinctrl_data`, selected by `meson_gxl_pinctrl_dt_match`. Both use `meson8_pmx_ops`; the AO data uses `meson8_aobus_parse_dt_extra`. Static data includes pin descriptor arrays, Meson8-style group arrays, function arrays, and GPIO bank arrays built with `BANK()`.

Control flow: The platform driver matches `amlogic,meson-gxl-periphs-pinctrl` or `amlogic,meson-gxl-aobus-pinctrl`, then delegates to `meson_pinctrl_probe()`. At runtime, pinctrl state application uses `meson8_pmx_ops` to set the mux bits encoded in each group. GPIO, pull, direction, output, input, and IRQ handling come from the shared Meson core using this file's bank descriptors.

State and persistence: This file stores immutable hardware-description tables. Register state persists in mux and GPIO hardware. Periphs banks are X, DV, H, Z, CARD, BOOT, and CLK. AO bank coverage is GPIOAO_0..GPIOAO_9, unlike GXBB's larger AO range. No drive-strength register descriptors are supplied in these legacy `BANK()` entries.

Dependencies and integration points: Depends on `dt-bindings/gpio/meson-gxl-gpio.h`, `pinctrl-meson.h`, and `pinctrl-meson8-pmx.h`. Periphs functions include eMMC/NOR/SPI/SDCard/SDIO/NAND, UART A/B/C, I2C A/B/C/D, Ethernet and Ethernet LED pins, PWM A-F, HDMI hotplug/I2C, I2S output, SPDIF output, and TSIN A/B with alternate placements. AO functions include AO UARTs, AO I2C and slave I2C, remote input, AO PWM A/B, AO I2S/SPDIF output, and CEC.

Risks: GXL differs from GXBB in bank sizes and group availability despite similar structure; copying board pinctrl data between them can select nonexistent or different pins. AO pin count is smaller, so GXBB AO group assumptions are unsafe. Legacy mux group data must be interpreted by `meson8_pmx_ops`, not AXG ops. Ethernet LED and TSIN alternate groups share pins with other peripherals and need board-level conflict review.

Test signals: Build and boot on GXL hardware using both compatible strings. Verify pinctrl function/group enumeration against DTS, mux storage and network peripherals, HDMI/CEC, I2S/SPDIF, TSIN, UART/I2C/SPI, PWM, Ethernet LEDs, and AO remote/PWM/CEC functions. Test GPIO input/output, pulls, and IRQs across each bank, especially AO and GXL-specific H/Z/X differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-gxl.c -->
