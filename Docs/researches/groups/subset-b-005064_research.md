# Research Group: subset-b-005064

This grouped report covers Linux kernel pinctrl drivers and build glue under Amlogic Meson, Microchip PolarFire/PIC64GX, and Marvell MVEBU paths. Each section preserves the source path and is bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-s4.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-s4.c

## Purpose
This file is the Amlogic Meson S4 peripheral-bank pin controller description. It does not implement a new pinctrl algorithm; instead it provides the SoC-specific pin, group, function, GPIO bank, pinmux-bank, device-tree match, and platform-driver data consumed by the shared Meson core in `pinctrl-meson.c` and the AXG-style mux backend.

## Important APIs, Types, and Data
- `meson_s4_periphs_pins` enumerates S4 pins from GPIOE/GPIOB/GPIOC/GPIOD/GPIOH/GPIOX/GPIOZ plus `GPIO_TEST_N` using the common `MESON_PIN()` macro.
- Hundreds of `*_pins` arrays define single-pin or multi-pin pinmux groups for peripherals such as I2C, UART, eMMC/NAND, SPI flash, SD card, JTAG, PDM, TDM, PWM, HDMI TX, CEC, SPDIF, Ethernet, DTV/TSIN, DiSEqC, and demod GPIOs.
- `meson_s4_periphs_groups` maps those arrays to AXG mux encodings through `GROUP()` from `pinctrl-meson-axg-pmx.h`; the group entries encode bank-relative function selectors rather than first-generation bit enables.
- `meson_s4_periphs_functions` groups pin groups into Linux pinmux functions via `FUNCTION()`.
- `meson_s4_periphs_banks` uses `BANK_DS()` to describe pull-enable, pull direction, GPIO direction, output, input, and drive-strength registers per bank.
- `meson_s4_periphs_pmx_banks` and `meson_s4_periphs_pmx_banks_data` describe the mux register layout for the AXG mux backend.
- `meson_s4_periphs_pinctrl_data` binds all tables to `meson_axg_pmx_ops`, `meson_a1_parse_dt_extra`, and the common `meson_pinctrl_probe()`.
- `meson_s4_pinctrl_dt_match` exposes `amlogic,meson-s4-periphs-pinctrl`; `meson_s4_pinctrl_driver` registers as a module platform driver.

## Control Flow
At probe, the platform core matches the S4 compatible and passes `meson_s4_periphs_pinctrl_data` to `meson_pinctrl_probe()`. The common Meson probe maps register resources from the GPIO child node, applies the S4 parse hook, registers a pinctrl device with AXG mux ops, and registers a GPIO chip. Runtime mux selections flow through the AXG backend using each group entry and `meson_s4_periphs_pmx_banks`; pin configuration and GPIO direction/value flow through the common bank register descriptors.

## State and Persistence
The file is static SoC description data. Runtime state lives in hardware registers reached through regmap. Because `parse_dt` is `meson_a1_parse_dt_extra`, S4 reuses the GPIO regmap for pull, pull-enable, and drive-strength spaces after the normal DT parse. No software persistence, suspend/resume state, or dynamic allocation is implemented in this file.

## Dependencies and Integration Points
The driver depends on `dt-bindings/gpio/meson-s4-gpio.h` for pin numbers, `pinctrl-meson.h` for common data structures, and `pinctrl-meson-axg-pmx.h` for AXG group and bank mux definitions. It integrates with device tree through the S4 compatible and with Linux pinctrl, pinmux, pinconf, and gpiolib through the shared Meson core.

## Risks
The main risk is table accuracy: incorrect pin numbers, group membership, mux register offsets, mux function values, or `BANK_DS()` offsets would silently route board pins to the wrong peripheral or break GPIO/pinconf operations. The `GPIO_TEST_N` bank has no IRQ range (`-1, -1`) and should remain isolated from GPIO interrupt assumptions. The S4 parse hook's shared-regmap behavior must match the binding and hardware; a DT/resource mismatch would affect pull and drive-strength programming globally.

## Test Signals
Useful signals are kernel build coverage with `CONFIG_PINCTRL_MESON`, DT binding validation for `amlogic,meson-s4-periphs-pinctrl`, boot-time successful pinctrl/gpiochip registration, debugfs pinmux listings, and hardware smoke tests for representative shared pins: eMMC/NAND, SD card, UART, I2C, Ethernet, HDMI/CEC, PWM, and GPIO direction/value/pull/drive-strength changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-s4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson.c

## Purpose
This is the shared Amlogic Meson pinctrl and GPIO core. It implements generic Linux pinctrl group reporting, shared function enumeration helpers, generic pin configuration, GPIO chip operations, MMIO regmap mapping from device tree, SoC-specific parse hooks, and the common probe used by Meson SoC table files.

## Important APIs, Types, and Functions
- `meson_get_bank()` locates the bank descriptor containing a pin.
- `meson_calc_reg_and_bit()` translates a pin and `enum meson_reg_type` into a byte register offset and bit index, including two-bit drive-strength stride handling.
- `meson_pctrl_ops` exposes group count/name/pins, generic DT map parsing, map freeing, and debug display.
- Exported pinmux helpers `meson_pmx_get_funcs_count()`, `meson_pmx_get_func_name()`, and `meson_pmx_get_groups()` are reused by Meson mux backends.
- Pinconf helpers program GPIO direction/output, pull-enable/pull-up/down, and optional drive strength.
- `meson_pinconf_ops` implements generic pinconf get/set and group set.
- GPIO callbacks implement direction, input, output, get, set, and registration through `gpiochip_add_data()`.
- `meson_map_resource()` maps named MMIO resources (`mux`, `gpio`, `pull`, `pull-enable`, `ds`) into regmaps.
- `meson_pinctrl_parse_dt()` validates one GPIO child node, maps resources, and invokes optional SoC parse hooks.
- Exported parse hooks `meson8_aobus_parse_dt_extra()` and `meson_a1_parse_dt_extra()` adapt older AO and newer shared-register layouts.
- `meson_pinctrl_probe()` allocates state, parses DT, registers pinctrl, and then registers the GPIO chip.

## Control Flow
Probe allocates `struct meson_pinctrl`, stores match data, parses the GPIO child node and resources, sets up a `pinctrl_desc`, registers the pinctrl device, and adds a GPIO chip. Pinctrl queries read directly from the SoC static tables. Pin configuration calls find the relevant bank, calculate register/bit positions, and update regmaps. GPIO calls reuse pinconf helpers so direction and output are consistently represented. Mux operations are delegated to `pc->data->pmx_ops`, allowing first-generation and AXG-style backends to share this core.

## State and Persistence
Persistent driver state is `struct meson_pinctrl`, held for the device lifetime and containing regmaps, the pinctrl device, GPIO chip, fwnode, and SoC data pointer. Pin state persists in hardware registers, not in software. The file does not implement suspend/resume save/restore. Group pinconf set ignores per-pin errors while iterating, which can hide partial group configuration failures.

## Dependencies and Integration Points
This core depends on Linux pinctrl, pinmux, pinconf-generic, gpiolib, device-tree address translation, platform devices, and regmap MMIO. It is integrated by SoC files that populate `struct meson_pinctrl_data` and call `meson_pinctrl_probe()` from their platform driver. It exports helper symbols for Meson mux backends and parse hooks.

## Risks
Resource naming and GPIO child-node structure are strict: missing `mux` or `gpio` resources fail probe, while absent pull or drive-strength resources disable related features. `meson_regmap_config` is a mutable static updated per resource, so correctness relies on probe-time serialization conventions. Drive-strength values are rounded up to supported hardware values and invalid high values warn once then default to 4 mA. `meson_gpio_get()` ignores the `regmap_read()` return value after calculating the bank, risking stale `val` usage if the read fails.

## Test Signals
Build with Meson SoC drivers and exercise boot probing for old AO, newer shared-register, and drive-strength-capable SoCs. Runtime checks should cover pinconf get/set for bias, output-enable, output level, and drive-strength; GPIO direction/value via gpiolib; DT parsing failures for missing resources; and debugfs group/function visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson.h

## Purpose
This header defines the shared data model and helper macros used by Amlogic Meson pinctrl SoC descriptions and mux backends. It is the contract between table-only SoC files, common pinctrl/pinconf/GPIO code, and pinmux implementations.

## Important APIs, Types, and Macros
- `struct meson_pmx_group` names a pin group, lists its pins, and carries backend-specific mux data in `data`.
- `struct meson_pmx_func` maps a function name to its supported group names.
- `struct meson_reg_desc` and `enum meson_reg_type` describe bank-local register/bit starts for pull-enable, pull, direction, output, input, and drive-strength.
- `enum meson_pinconf_drv` defines encoded drive-strength values for 500 uA, 2500 uA, 3000 uA, and 4000 uA.
- `struct meson_bank` maps a contiguous pin range to register descriptors and IRQ metadata.
- `struct meson_pinctrl_data` packages SoC static data, mux ops, mux-private data, and optional DT parse hook.
- `struct meson_pinctrl` is the per-device runtime state shared by the core and backends.
- `FUNCTION()`, `BANK_DS()`, `BANK()`, and `MESON_PIN()` reduce boilerplate in SoC table files.
- Function declarations expose shared mux enumeration helpers, common probe, and parse hooks.

## Control Flow
This file has no executable control flow. Its structures drive runtime control flow elsewhere: SoC probe match data points to `meson_pinctrl_data`, common pinconf uses `meson_bank.regs`, and mux backends interpret `meson_pmx_group.data`.

## State and Persistence
The header defines the lifetime-bearing `struct meson_pinctrl`; actual allocation occurs in `meson_pinctrl_probe()`. Static SoC data generally has built-in or module lifetime. Hardware state persists in registers referenced by regmaps in `struct meson_pinctrl`.

## Dependencies and Integration Points
It includes Linux GPIO, pinctrl, platform device, regmap, types, and module headers. It is included by Meson common code, first-generation mux code, AXG mux code, and SoC data files.

## Risks
Macro argument order in `BANK_DS()` and `BANK()` is dense and easy to misuse; an offset transposition changes pinconf or GPIO behavior across a bank. `struct meson_pmx_group.data` is untyped, so each backend must cast it consistently. Drive-strength encodings and bit stride assumptions must remain synchronized with `meson_bit_strides` in the core.

## Test Signals
Compiler coverage across all Meson SoC files is the primary signal for structural compatibility. Runtime signals come from successful probe, correct group/function enumeration, and pinconf/GPIO behavior on representative SoCs using different mux backends and register-sharing parse hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8-pmx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8-pmx.c

## Purpose
This file implements the first-generation Amlogic Meson pinmux backend used by Meson8-era SoCs. In this hardware model, each non-GPIO pinmux group is enabled by a specific bit in the mux register range; GPIO mode is achieved by disabling all alternate groups that use the pin.

## Important APIs, Types, and Functions
- `meson8_pmx_disable_other_groups()` scans all groups, finds groups sharing a pin, and clears their mux enable bit unless they are GPIO groups or the selected group.
- `meson8_pmx_set_mux()` disables conflicting groups for every pin in the selected group, then sets the selected group's mux bit for non-GPIO functions.
- `meson8_pmx_request_gpio()` disables all alternate groups for a requested GPIO pin.
- `meson8_pmx_ops` exposes set-mux, common function enumeration helpers, and GPIO-request handling.

## Control Flow
When pinctrl selects a function/group, `meson8_pmx_set_mux()` retrieves the function and group from the shared SoC tables, casts `group->data` to `struct meson8_pmx_data`, disables other groups sharing each selected pin, and writes the selected bit if the function selector is nonzero. GPIO requests call the same conflict-disabling routine with no selected group.

## State and Persistence
The backend keeps no private runtime state. It mutates mux hardware through `pc->reg_mux`; selected functions persist in hardware registers. The code avoids clearing the selected group before setting it, reducing output glitches while changing muxes.

## Dependencies and Integration Points
It depends on `struct meson_pinctrl`, shared function helpers from `pinctrl-meson.c`, and `struct meson8_pmx_data` from `pinctrl-meson8-pmx.h`. Meson8 and Meson8b SoC files point their `pmx_ops` at `meson8_pmx_ops`.

## Risks
Conflict resolution is an O(groups * pins-per-group) scan, acceptable for small tables but dependent on accurate group pin lists. If a GPIO group is not marked `is_gpio`, it may be treated as an alternate function. The code uses `func_num == 0` as the GPIO convention, so SoC function arrays must keep GPIO first. `regmap_update_bits()` return values from conflict clearing are ignored inside `meson8_pmx_disable_other_groups()`.

## Test Signals
Exercise mux changes on pins with multiple alternate functions, GPIO requests after peripheral use, and boot-time group/function enumeration for Meson8 and Meson8b. Dynamic debug logs from `set_mux` and visible mux bits through debugfs/register inspection are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8-pmx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8-pmx.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8-pmx.h

## Purpose
This header defines the first-generation Meson8 pinmux group metadata and table macros used by Meson8 and Meson8b SoC description files.

## Important APIs, Types, and Macros
- `struct meson8_pmx_data` stores whether a group is GPIO plus the mux register index and bit.
- `PMX_DATA()` initializes backend-specific mux metadata.
- `GROUP()` creates a named non-GPIO `struct meson_pmx_group` using a `*_pins` array and a compound-literal `meson8_pmx_data`.
- `GPIO_GROUP()` creates a one-pin GPIO group with `is_gpio = true`.
- `extern const struct pinmux_ops meson8_pmx_ops` exports the backend operations to SoC files.

## Control Flow
No executable code is present. The macros shape static group arrays that `pinctrl-meson8-pmx.c` later scans and casts.

## State and Persistence
The macro-produced data has static storage as part of SoC group tables, while the compound-literal metadata is const table data. Hardware mux state is changed by the backend, not this header.

## Dependencies and Integration Points
The macros assume `ARRAY_SIZE()` and `struct meson_pmx_group` are available through the includer. Meson8-family SoC files include this after `pinctrl-meson.h`.

## Risks
The untyped `data` field requires correct casting in the backend. The `GROUP()` macro expects a matching `grp_pins` symbol; typos fail at compile time, but wrong register/bit values compile and misconfigure hardware. `GPIO_GROUP()` uses dummy register/bit values, so `is_gpio` must be honored everywhere.

## Test Signals
Compile all Meson8-family SoC tables and verify debugfs lists GPIO and alternate groups. Runtime mux tests should confirm that each group writes the intended register bit and GPIO groups do not write mux bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8-pmx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8.c

## Purpose
This file describes the Amlogic Meson8 and Meson8m2 pin controllers for CBUS and AO bus domains. It supplies static pin, group, function, and bank tables to the shared Meson core and first-generation Meson8 mux backend.

## Important APIs, Types, and Data
- `meson8_cbus_pins` covers GPIOX/Y/DV/H/Z, CARD, and BOOT pins; `meson8_aobus_pins` covers GPIOAO plus special always-on pins.
- Pin arrays and group tables define SD/SDXC, PCM, UART, ISO7816, I2C, XTAL, DVI/ENC/VGA/HDMI, SPI, Ethernet, NAND/NOR, PWM, I2S, SPDIF, remote, AO I2C, and HDMI CEC functions.
- `meson8_cbus_functions` and `meson8_aobus_functions` expose functions with GPIO first, matching first-generation mux backend expectations.
- `meson8_cbus_banks` and `meson8_aobus_banks` encode register offsets/bits for pull, GPIO direction/value/input, and IRQ ranges.
- `meson8_cbus_pinctrl_data` and `meson8_aobus_pinctrl_data` bind the static data to `meson8_pmx_ops`; AO uses `meson8_aobus_parse_dt_extra`.
- `meson8_pinctrl_dt_match` covers Meson8 and Meson8m2 CBUS/AOBUS compatibles; the driver is built in with `builtin_platform_driver()`.

## Control Flow
Device-tree matching selects either CBUS or AOBUS data, then the shared probe maps resources and registers pinctrl/gpio. Mux selection is handled by `meson8_pmx_ops`, which reads each group’s register bit metadata. Pinconf and GPIO operations use the bank descriptors in this file. AO parsing aliases pull-enable to the pull register range because older AO layouts share those registers.

## State and Persistence
This is static SoC data only. Hardware registers retain mux, pull, and GPIO state. No local dynamic state or suspend/resume logic is implemented.

## Dependencies and Integration Points
It depends on `dt-bindings/gpio/meson8-gpio.h`, `pinctrl-meson.h`, and `pinctrl-meson8-pmx.h`. It integrates with DT compatibles `amlogic,meson8-cbus-pinctrl`, `amlogic,meson8-aobus-pinctrl`, `amlogic,meson8m2-cbus-pinctrl`, and `amlogic,meson8m2-aobus-pinctrl`.

## Risks
The CBUS/AOBUS split requires board DTS nodes to bind the correct compatible and resources. Function ordering must keep GPIO at selector zero. Dense `GROUP()` register/bit tables and `BANK()` register descriptors are susceptible to silent hardware misrouting if copied incorrectly. AO register sharing depends on `meson8_aobus_parse_dt_extra()` and requires the pull resource to be present.

## Test Signals
Boot Meson8 and Meson8m2 boards with both CBUS and AOBUS nodes, validate gpiochip counts, inspect pinctrl debugfs function/group lists, and smoke-test UART/I2C/SD/NAND/Ethernet/HDMI CEC/AO remote pins. GPIO request tests should confirm alternate mux bits are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8b.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8b.c

## Purpose
This file describes the Amlogic Meson8b CBUS and AOBUS pin controllers. It is a static SoC data provider for the shared Meson pinctrl core and first-generation mux backend.

## Important APIs, Types, and Data
- `meson8b_cbus_pins` lists GPIOX/Y/DV/H/CARD/BOOT/DIF pins, with gaps reflecting the public SoC pin map.
- `meson8b_aobus_pins` lists GPIOAO pins plus `GPIO_BSD_EN` and `GPIO_TEST_N`, with comments noting undocumented pins.
- Pin group tables cover SD/SDXC, PCM, UART, ISO7816, SPI, TSIN, PWM, I2C, HDMI, Ethernet, NAND/NOR, SPDIF, I2S, remote, clock, and HDMI CEC functions.
- `meson8b_cbus_functions` and `meson8b_aobus_functions` expose function groupings, with GPIO as the first selector.
- `meson8b_cbus_banks` uses fine-grained bank ranges such as `X0..11`, `X16..21`, `Y0..1`, and `DIF`; `meson8b_aobus_banks` describes AO pins.
- Pinctrl data structures point to `meson8_pmx_ops`; AOBUS uses `meson8_aobus_parse_dt_extra`.
- `meson8b_pinctrl_dt_match` exposes CBUS and AOBUS compatibles and registers a built-in platform driver.

## Control Flow
The platform driver uses the shared Meson probe. Runtime mux requests go through the first-generation backend, using per-group bit metadata to clear conflicting groups and enable the selected group. Pinconf/GPIO calls use the common Meson bank register calculation based on the ranges in this file.

## State and Persistence
The file holds immutable tables. Mux, pull, direction, and GPIO values persist in hardware registers. No local state machine or save/restore path is present.

## Dependencies and Integration Points
It depends on `dt-bindings/gpio/meson8b-gpio.h`, the Meson common header, and the Meson8 mux header. Device-tree integration is through `amlogic,meson8b-cbus-pinctrl` and `amlogic,meson8b-aobus-pinctrl`.

## Risks
Meson8b has discontinuous pin ranges and undocumented pins; incorrect bank boundaries or IRQ ranges can affect GPIO numbering or interrupt assumptions. The DIF bank is marked with unknown IRQ support (`-1, -1`) and should not be assumed interrupt-capable. The first-generation mux backend relies on complete group pin overlap data to avoid conflicts.

## Test Signals
Build and boot with Meson8b DT nodes, verify CBUS/AOBUS gpiochip registration and pinctrl debugfs output, and run hardware tests on shared-function pins such as SD/SDXC, UART, SPI, HDMI, Ethernet, NAND/NOR, AO remote, and GPIO fallback after peripheral muxing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/Kconfig

## Purpose
This Kconfig fragment declares Microchip pinctrl configuration symbols for PIC64GX GPIO2 and PolarFire SoC pinctrl drivers.

## Important APIs, Types, and Entries
- `PINCTRL_PIC64GX` is a bool for the PIC64GX GPIO2 pinctrl driver. It depends on `ARCH_MICROCHIP || COMPILE_TEST` and `OF`, and selects `GENERIC_PINCONF` plus `REGMAP_MMIO`.
- `PINCTRL_POLARFIRE_SOC` is a bool for PolarFire SoC pinctrl drivers. It depends on `ARCH_MICROCHIP || COMPILE_TEST` and `OF`, and selects `GENERIC_PINCTRL`.

## Control Flow
There is no runtime control flow. Kconfig selection controls which objects the Makefile includes and which pinctrl helper frameworks are guaranteed available at compile time.

## State and Persistence
The only state is build configuration. It persists in the kernel `.config` and determines built-in object inclusion because the symbols are bools.

## Dependencies and Integration Points
The entries integrate with architecture selection, device tree support, generic pinctrl/pinconf helpers, and the local Makefile. `PINCTRL_POLARFIRE_SOC` builds both IOMUX0 and MSSIO objects.

## Risks
`PINCTRL_POLARFIRE_SOC` selects `GENERIC_PINCTRL` but the MSSIO driver also uses generic pinconf APIs and custom params; build coverage must ensure transitive pinconf availability is sufficient. Bool-only symbols mean these drivers are not independently modular from Kconfig even though the C files use `module_platform_driver()`.

## Test Signals
Run configuration/build tests with `ARCH_MICROCHIP`, with `COMPILE_TEST`, and with each symbol disabled/enabled. Confirm the expected objects appear in the build and no missing generic pinctrl/pinconf symbols occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/Makefile

## Purpose
This Makefile maps Microchip pinctrl Kconfig symbols to compiled driver objects.

## Important APIs, Types, and Entries
- `obj-$(CONFIG_PINCTRL_PIC64GX) += pinctrl-pic64gx-gpio2.o`
- `obj-$(CONFIG_PINCTRL_POLARFIRE_SOC) += pinctrl-mpfs-iomux0.o`
- `obj-$(CONFIG_PINCTRL_POLARFIRE_SOC) += pinctrl-mpfs-mssio.o`

## Control Flow
There is no runtime control flow. Kbuild includes objects based on the evaluated `CONFIG_*` variables.

## State and Persistence
Build state comes from the kernel configuration. No runtime state is defined here.

## Dependencies and Integration Points
It integrates the local Kconfig symbols with Kbuild and the C driver files in the same directory.

## Risks
`CONFIG_PINCTRL_POLARFIRE_SOC` always builds both PolarFire pinctrl objects together; platforms needing only one still compile both. Object names must stay synchronized with source filenames and Kconfig symbol names.

## Test Signals
Use `make drivers/pinctrl/microchip/` or full kernel builds with each symbol toggled. Confirm the object list matches the Kconfig selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-mpfs-iomux0.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-mpfs-iomux0.c

## Purpose
This driver controls the PolarFire SoC IOMUX0 register that selects whether fixed peripheral interfaces are connected to MSSIO pins or FPGA fabric. It presents each peripheral as a pin/function with two groups: `<name>_mssio` and `<name>_fabric`.

## Important APIs, Types, and Functions
- `MPFS_IOMUX0_REG` is the syscon register offset (`0x200`) containing one selection bit per peripheral.
- `struct mpfs_iomux0_pinctrl` stores pinctrl device, device pointer, syscon regmap, and descriptor.
- `struct mpfs_iomux0_pin_group` stores group name, one-pin list, mask, and setting.
- `struct mpfs_iomux0_function` maps a function to its two groups.
- `MPFS_IOMUX0_GROUP()` generates MSSIO/fabric group pairs.
- Pinctrl ops expose group count/name/pins, generic DT map conversion, and debug display.
- Pinmux ops expose function enumeration and `mpfs_iomux0_pinmux_set_mux()`, which writes the group mask/setting with `regmap_assign_bits()`.
- `mpfs_iomux0_probe()` gets the parent syscon regmap, fills the descriptor, and registers pinctrl.

## Control Flow
Probe obtains the parent node's regmap and registers a pinctrl device. Device-tree pinctrl states map to one of the generated groups. On mux selection, the selected group directly writes its bit in `MPFS_IOMUX0_REG`: zero selects MSSIO and one selects fabric for that peripheral. Debug display reads the same bit for a pin.

## State and Persistence
Runtime software state is the small `mpfs_iomux0_pinctrl` allocation. Selection state persists in the syscon register. There is no suspend/resume save/restore and no software cache.

## Dependencies and Integration Points
The driver depends on syscon/regmap, platform devices, OF matching, generic pinctrl/pinmux helpers, and pinconf DT map helpers. It binds to `microchip,mpfs-pinctrl-iomux0` and expects its parent DT node to provide a syscon regmap.

## Risks
`mpfs_iomux0_probe()` calls `dev_err_probe()` when `device_node_to_regmap()` fails but does not return the error, leaving an `ERR_PTR` regmap available for later registration and operations. That can turn a probe-time resource failure into later invalid regmap use. The function-to-group relation assumes every function has exactly two groups. All selection writes are bit-level and lack locking beyond regmap internals.

## Test Signals
Build with `CONFIG_PINCTRL_POLARFIRE_SOC`, boot with `microchip,mpfs-pinctrl-iomux0`, verify probe fails cleanly when the parent syscon is absent, and use pinctrl states to switch SPI/I2C/CAN/QSPI/UART/MDIO interfaces between MSSIO and fabric while reading back the IOMUX0 register or debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-mpfs-iomux0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-mpfs-mssio.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-mpfs-mssio.c

## Purpose
This driver implements PolarFire SoC MSSIO pinmux and pin configuration for 38 pins across MSS banks 4 and 2. It supports per-pin mux function selection, bias, drive strength, Schmitt input, low-power/persist settings, bank voltage selection, and Microchip-specific clamp/IBUF mode bindings.

## Important APIs, Types, and Functions
- Register masks define pad mux, IOCFG fields, bank voltage fields, low-power bits, clamp, lockdown, weak pull-up/down, hysteresis, and drive strength.
- `struct mpfs_pinctrl` stores pinctrl device, regmap for pinctrl syscon, sysreg regmap for bank voltage, mutex, and descriptor.
- `mpfs_pinctrl_drive_strengths` maps hardware drive encodings to mA values; `mpfs_pinctrl_bank_voltages` maps sysreg encodings to microvolts.
- Conversion helpers map requested drive strength and voltage to hardware encodings and back.
- `mpfs_pinctrl_pin_to_iomux_reg()/offset()` and `mpfs_pinctrl_pin_to_iocfg_reg()/offset()` translate pin numbers to register fields.
- `mpfs_pinctrl_set_mux()` uses generic groups and per-pin function strings from DT to write mux functions.
- `mpfs_pinctrl_pinconf_get()` reads generic and custom configs.
- `mpfs_pinctrl_pinconf_generate_config()` converts packed configs into IOCFG register bits and optional bank voltage.
- `mpfs_pinctrl_pinconf_set()` and group set write IOCFG fields and bank voltage.
- `mpfs_pinctrl_probe()` gets parent and sysreg regmaps, initializes descriptor operations and custom params, and registers pinctrl.

## Control Flow
Device-tree mapping uses `pinctrl_generic_pins_function_dt_node_to_map`, so groups and functions are created by generic helpers from DT. Mux setting retrieves a generic group, maps each function string through `mpfs_pinctrl_function_map()`, computes register/offset, and updates the pad mux field. Pinconf set builds a replacement IOCFG value from supplied configs, writes the 15-bit field for each target pin, then updates bank voltage if requested. Pinconf get reads the current field and validates whether the requested config is active.

## State and Persistence
Driver state is `struct mpfs_pinctrl`; hardware mux/config/voltage state persists in syscon registers. The code initializes a mutex but does not use it around register updates. There is no suspend/resume path. Group voltage changes assume all pins in a group belong to the same bank, matching a driver comment about MSS Configurator constraints.

## Dependencies and Integration Points
The driver integrates with parent syscon regmap, the `microchip,mpfs-sysreg-scb` sysreg compatible for bank voltage, Linux generic pinctrl/pinmux/pinconf, custom pinconf parameters, and the `microchip,mpfs-pinctrl-mssio` compatible.

## Risks
`mpfs_pinctrl_pinconf_generate_config()` starts from zero rather than the current IOCFG field, so a partial pinconf update clears unspecified fields. Bank voltage conversion uses a sorted table with an unused sentinel; requests above supported voltages return `-EINVAL`. `MPFS_PINCTRL_LOCKDOWN` is readable but not listed in `mpfs_pinctrl_custom_bindings`, so external DT naming for that custom config is not exposed here. Register write return values from some helpers are not checked. The unused mutex suggests intended serialization that is not enforced beyond regmap behavior.

## Test Signals
Build with `CONFIG_PINCTRL_POLARFIRE_SOC` and validate DT states that assign pin groups and per-pin functions. Test pinconf round trips for pull-up, pull-down, bus-hold, bias-disable, drive-strength, Schmitt, persist, low-power, power-source, clamp, and ibufmd. Hardware validation should read IOCFG and bank voltage registers after DT application and verify group updates across both bank 4 and bank 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-mpfs-mssio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-pic64gx-gpio2.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-pic64gx-gpio2.c

## Purpose
This driver controls the PIC64GX GPIO2 pinmux register. It exposes package pins and peripheral groups where each group can be selected either as GPIO or as a fixed peripheral function by setting bits in a single MMIO register.

## Important APIs, Types, and Functions
- `PIC64GX_PINMUX_REG` is the single mux register at offset zero.
- `pic64gx_gpio2_regmap_config` defines a little-endian 32-bit MMIO regmap.
- `pic64gx_gpio2_pins` names 29 package pins by ball labels.
- Group arrays cover MDIO0/1, SPI0, CAN0/1, PCIe, QSPI, UART3/4/2.
- `PIC64GX_PINCTRL_GROUP()` generates paired GPIO/peripheral groups for each function, with group-specific masks and settings.
- `pic64gx_gpio2_functions` maps function names to group lists, including a multi-group `gpio` function.
- Pinctrl ops expose group metadata and debug display; pinmux ops expose function metadata and write selected group settings.
- `pic64gx_gpio2_probe()` maps MMIO resource 0, creates a regmap, initializes the descriptor, and registers pinctrl.

## Control Flow
Probe maps the hardware register and registers the pinctrl device. DT pinctrl states select a function/group; `pic64gx_gpio2_pinmux_set_mux()` looks up the selected group and writes its mask/setting using `regmap_assign_bits()`. GPIO groups clear the same bits that peripheral groups set.

## State and Persistence
Software state is `struct pic64gx_gpio2_pinctrl`. Mux selections persist in the single MMIO register. There is no pinconf, GPIO chip, IRQ handling, or suspend/resume state in this file.

## Dependencies and Integration Points
The driver depends on platform MMIO resources, regmap MMIO, Linux pinctrl/pinmux helpers, generic DT map parsing, and the `microchip,pic64gx-pinctrl-gpio2` compatible. It is selected by `CONFIG_PINCTRL_PIC64GX`.

## Risks
The whole driver is table driven around one register, so incorrect bit masks or package-pin group membership will misroute peripherals. There is no GPIO-controller implementation here despite the `gpio_` group names; it only selects mux mode. `regmap_assign_bits()` return values are not checked in `set_mux`.

## Test Signals
Build with `CONFIG_PINCTRL_PIC64GX`, verify the platform resource maps, inspect debugfs pinctrl groups/functions, and test switching each peripheral group to GPIO and peripheral mode while reading back the mux register. Board-level validation should cover QSPI, CAN, UART, MDIO, SPI, and PCIe reset/sideband pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-pic64gx-gpio2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/Kconfig

## Purpose
This Kconfig fragment declares Marvell MVEBU pinctrl support symbols for the shared MVEBU core and SoC-specific drivers.

## Important APIs, Types, and Entries
- `PINCTRL_MVEBU` is the common bool selected by legacy MVEBU table drivers and selects `PINMUX` and `PINCONF`.
- SoC bools `PINCTRL_DOVE`, `PINCTRL_KIRKWOOD`, `PINCTRL_ARMADA_370`, `PINCTRL_ARMADA_375`, `PINCTRL_ARMADA_38X`, `PINCTRL_ARMADA_39X`, `PINCTRL_ARMADA_AP806`, `PINCTRL_ARMADA_CP110`, `PINCTRL_ARMADA_XP`, `PINCTRL_ORION`, and `PINCTRL_AC5` select `PINCTRL_MVEBU`; Dove also selects `MFD_SYSCON`.
- `PINCTRL_ARMADA_37XX` is separate and selects `GENERIC_PINCONF`, `MFD_SYSCON`, `PINCONF`, and `PINMUX`.

## Control Flow
No runtime control flow exists. These symbols decide which objects Kbuild compiles and which frameworks are selected.

## State and Persistence
State is build configuration only. The bool symbols typically build the selected pinctrl drivers into the kernel image.

## Dependencies and Integration Points
The fragment integrates MVEBU platform/SoC symbols from architecture code with the local Makefile and shared pinctrl frameworks.

## Risks
Most SoC symbols have no explicit architecture or OF dependency in this fragment, so they are expected to be selected by platform Kconfig rather than manually configured. Armada 37xx bypasses `PINCTRL_MVEBU`, which is correct for its custom driver but means shared-core assumptions do not apply.

## Test Signals
Kernel config/build tests should verify each SoC symbol pulls in the right object and framework symbols. `COMPILE_TEST` coverage must come from parent Kconfig selections if desired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/Makefile

## Purpose
This Makefile maps MVEBU pinctrl Kconfig symbols to the shared core object and SoC-specific pinctrl driver objects.

## Important APIs, Types, and Entries
- `obj-$(CONFIG_PINCTRL_MVEBU) += pinctrl-mvebu.o` builds the shared legacy MVEBU core.
- SoC entries build Dove, Kirkwood, Armada 370/375/38x/39x/AP806/CP110/XP, Armada 37xx, Orion, and AC5 objects according to their Kconfig symbols.

## Control Flow
There is no runtime control flow. Kbuild uses the evaluated `CONFIG_*` variables to include objects.

## State and Persistence
Build state is held in `.config`. No runtime state is represented here.

## Dependencies and Integration Points
It must stay synchronized with `Kconfig` and source filenames. Most listed SoC drivers depend on `pinctrl-mvebu.o`; Armada 37xx is included separately by its own symbol.

## Risks
If a SoC symbol is enabled without the expected shared core selection, link failures can occur; current Kconfig selections handle the legacy drivers. Formatting differences are benign, but object naming drift would break builds.

## Test Signals
Build with each `CONFIG_PINCTRL_*` symbol enabled and disabled, and confirm object inclusion with Kbuild verbose output or `make drivers/pinctrl/mvebu/`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-ac5.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-ac5.c

## Purpose
This file is the Marvell AC5 pinctrl SoC table driver. It describes AC5 multi-purpose pin (MPP) modes and passes them to the shared MVEBU pinctrl core.

## Important APIs, Types, and Data
- `ac5_mpp_modes` lists MPP pins 0 through 45 and their alternate functions, including GPIO, SDIO, NAND, SPI0/1, UARTs, I2C, MDIO, PTP, watchdog/interrupt lines, PCIe reset, syncE, and LED signals.
- `ac5_pinctrl_info` is the shared `mvebu_pinctrl_soc_info` filled at probe.
- `ac5_pinctrl_of_match` binds `marvell,ac5-pinctrl`.
- `ac5_mpp_controls` declares one MMIO MPP control covering pins 0-45 via `mvebu_mmio_mpp_ctrl`.
- `ac5_mpp_gpio_ranges` exposes all 46 pins as a GPIO range.
- `ac5_pinctrl_probe()` fills the SoC info and delegates to `mvebu_pinctrl_simple_mmio_probe()`.

## Control Flow
On platform probe, the driver initializes `ac5_pinctrl_info` with variant zero, control descriptors, GPIO ranges, mode table, and mode count, stores it in `pdev->dev.platform_data`, and calls the shared simple MMIO probe. Runtime muxing is implemented by the shared MVEBU core using these tables.

## State and Persistence
This file contains static mode/control data plus one static SoC info structure populated during probe. MPP state persists in hardware registers managed by the shared core. No local suspend/resume or dynamic state is implemented.

## Dependencies and Integration Points
It depends on `pinctrl-mvebu.h`, platform devices, OF matching, and the shared MVEBU MMIO control helpers. It is built when `CONFIG_PINCTRL_AC5` is selected.

## Risks
The driver assumes a single contiguous control range for all 46 pins. Incorrect MPP mode values or GPIO range length would cause wrong peripheral routing. `soc->nmodes` is derived from `ac5_mpp_controls[0].npins`, so it must match the populated `ac5_mpp_modes` entries.

## Test Signals
Build with `CONFIG_PINCTRL_AC5`, boot an AC5 DT using `marvell,ac5-pinctrl`, inspect pinctrl debugfs for MPP functions, and test representative muxes such as SDIO, NAND, SPI, UART, I2C, MDIO/PTP, LED, and GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-ac5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-370.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-370.c

## Purpose
This file provides the Marvell Armada 370 / MV88F6710 MPP mode table and probe glue for the shared MVEBU pinctrl core.

## Important APIs, Types, and Data
- `mv88f6710_mpp_modes` describes MPP pins 0-65 with alternate functions including GPIO/GPO, UARTs, I2C, GE0/GE1, SATA presence, TDM, audio, SD0, SPI0/1, PCIe clock request/reset, device bus, and TCLK.
- `armada_370_pinctrl_info` is populated at probe.
- `armada_370_pinctrl_of_match` binds `marvell,mv88f6710-pinctrl`.
- `mv88f6710_mpp_controls` declares a single MMIO function control over pins 0-65.
- `mv88f6710_mpp_gpio_ranges` exposes three GPIO ranges: 0-31, 32-63, and 64-65.
- `armada_370_pinctrl_probe()` fills SoC info and delegates to `mvebu_pinctrl_simple_mmio_probe()`.

## Control Flow
Probe writes the static mode/control/range data into `armada_370_pinctrl_info`, assigns it to platform data, and invokes the shared simple MMIO probe. The shared core handles pinctrl registration and runtime register writes.

## State and Persistence
Static mode data lives for the built-in driver lifetime. Hardware MPP selections persist in MMIO registers controlled by the shared core. No local software state beyond the SoC info structure is maintained.

## Dependencies and Integration Points
It depends on `pinctrl-mvebu.h`, OF platform matching, and the shared MVEBU MMIO controller implementation. Kbuild includes it through `CONFIG_PINCTRL_ARMADA_370`.

## Risks
The mode table is large and hardware-specific; wrong mode values can reroute boot-critical device bus, SPI, SD, SATA, or Ethernet pins. Some pins are GPO rather than GPIO-capable; consumers must not assume all ranges support input semantics beyond what the shared core/gpio ranges expose.

## Test Signals
Build and boot Armada 370 hardware/DT, verify debugfs MPP function lists, and exercise UART, I2C, SPI, SD, Ethernet, SATA presence, device bus, and GPIO operations. Cross-check GPIO range counts against DT GPIO controller expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-370.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-375.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-375.c

## Purpose
This file supplies the Marvell Armada 375 / MV88F6720 MPP mode table and probe glue for the shared MVEBU pinctrl core.

## Important APIs, Types, and Data
- `mv88f6720_mpp_modes` covers MPP pins 0-66 with functions for GPIO, device bus, SPI0/1, NAND, PTP, LEDs, audio, PCIe reset/clock request, I2C, UART, TDM, GE0/GE1, SD, SATA presence, DRAM VTT/error, and reference clock output.
- `armada_375_pinctrl_info` is the per-SoC info structure populated at probe.
- `armada_375_pinctrl_of_match` binds `marvell,mv88f6720-pinctrl`.
- `mv88f6720_mpp_controls` declares one MMIO MPP control range.
- `mv88f6720_mpp_gpio_ranges` exposes GPIO ranges for pins 0-31, 32-63, and 64-66.
- `armada_375_pinctrl_probe()` fills the SoC info and calls `mvebu_pinctrl_simple_mmio_probe()`.

## Control Flow
The platform probe stores mode/control/range tables into `armada_375_pinctrl_info`, attaches it to `pdev->dev.platform_data`, and delegates registration and runtime behavior to the shared MVEBU core.

## State and Persistence
The file defines static tables and one static SoC info structure. MPP state persists in hardware. No local dynamic state or suspend/resume handling is present.

## Dependencies and Integration Points
It depends on `pinctrl-mvebu.h`, platform/OF support, and Kconfig/Makefile selection through `CONFIG_PINCTRL_ARMADA_375`.

## Risks
The control descriptor uses `MPP_FUNC_CTRL(0, 69, ...)` while the visible mode table covers modes through 66 and GPIO ranges cover 67 pins; this may reflect hardware reserved pins but is a table consistency point to verify against the shared core and datasheet. Incorrect alternate values could break storage, PCIe, Ethernet, or boot bus pin routing.

## Test Signals
Build with `CONFIG_PINCTRL_ARMADA_375`, boot with `marvell,mv88f6720-pinctrl`, inspect pinctrl debugfs, and test representative SD, SPI, NAND, UART/I2C, PCIe reset/clkreq, GE, LED, and GPIO paths. Check for warnings or missing modes around the high MPP numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-37xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-37xx.c

## Purpose
This is a custom pinctrl, pinmux, GPIO, GPIO-IRQ, and power-management driver for Marvell Armada 37xx north-bridge and south-bridge pin controllers. Unlike older MVEBU table drivers, it does not use `pinctrl-mvebu.c`; it builds functions/groups dynamically from local group tables and directly manages GPIO and interrupt registers.

## Important APIs, Types, and Functions
- Register offsets define GPIO output enable/input/output/control, mux selection, IRQ enable/polarity/status/wakeup.
- `struct armada_37xx_pin_group` describes contiguous and optional extra pin ranges, mux mask/value choices, supported function names, and allocated pin lists.
- `struct armada_37xx_pin_data` describes NB or SB controller instances.
- `struct armada_37xx_pmx_func` is built dynamically from group function names.
- `struct armada_37xx_pm_state` saves GPIO, IRQ, and selection state across suspend.
- NB/SB group tables define functions such as JTAG, SDIO, eMMC, PWM/LED, PMIC, I2C, SPI, UART, one-wire, USB drive-vbus, RGMII/MII/SMI, PCIe, and PTP.
- Pinctrl ops expose group metadata; pinconf group get/set are unsupported.
- Pinmux ops implement function enumeration, group lookup, mux setting, GPIO request enable, and GPIO direction setting.
- GPIO callbacks implement direction, get, and set.
- IRQ chip callbacks implement ack, mask/unmask, wake, type setup, startup, print, both-edge polarity swapping, chained handling, and registration.
- `armada_37xx_pinctrl_register()` creates pin descriptors, fills group/function arrays, and registers pinctrl.
- Suspend/resume saves and restores GPIO, IRQ, and mux selection state, including both-edge IRQ polarity resynchronization.
- `armada_37xx_pinctrl_probe()` maps resources, creates regmap, registers pinctrl and GPIO chip, and stores driver data.

## Control Flow
Probe maps resource 0 for pinctrl registers, creates a raw-spinlock-enabled regmap, selects NB or SB pin data from DT match data, registers pinctrl, registers a GPIO chip, and optionally wires parent IRQs from the GPIO child node. During pinctrl registration, groups allocate concrete pin arrays and unique functions are counted, then each function gets its list of groups. Mux selection writes `SELECTION` bits using the selected group mask/value. GPIO requests force every group containing the pin into its `gpio` function. GPIO operations read/write register banks with `armada_37xx_update_reg()` to handle low/high register halves. IRQ handling scans enabled status bits, optionally flips polarity for both-edge emulation, and dispatches mapped child IRQs.

## State and Persistence
Runtime state is held in `struct armada_37xx_pinctrl`, including dynamically allocated functions, group pin arrays, gpio chip, IRQ lock, regmap, IRQ base, and saved PM state. Hardware register state persists until changed; suspend stores output enable/value, IRQ enable/polarity, and selection, then resume restores them and repairs both-edge polarity using current input levels.

## Dependencies and Integration Points
The driver depends on Linux pinctrl, pinmux, generic pinconf mapping, gpiolib, GPIO IRQ helpers, OF IRQ parsing, platform MMIO resources, regmap, and device PM. It binds `marvell,armada3710-sb-pinctrl` and `marvell,armada3710-nb-pinctrl`, expecting GPIO child-node information for gpiolib and optional parent interrupts.

## Risks
Pinconf is effectively unsupported despite generic pinconf ops being registered; DT users expecting electrical configuration will not get it here. Both-edge IRQ support is implemented by polarity toggling and depends on input-level races being handled correctly. `armada_37xx_irq_handler()` loops through `d->revmap_size / GPIO_PER_REG` inclusively, so bounds should be validated against actual domain sizes. `armada_37xx_gpio_direction_output()` reuses the output-value mask for output-enable after recomputing the register with a separate offset; this works only because the low/high bit index is equivalent, and should be treated carefully in modifications. IRQ registration returns success when no parent IRQ exists, leaving GPIO usable without interrupts.

## Test Signals
Boot NB and SB instances, verify pinctrl group/function enumeration, request GPIO on pins that belong to alternate groups, and test GPIO direction/value across pins below and above 32. IRQ tests should cover rising, falling, both-edge, wake enable, masked status filtering, and suspend/resume with changing input levels. PM tests should confirm mux selection and GPIO outputs survive suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-37xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-38x.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-38x.c

## Purpose
This file provides Marvell Armada 380/385/388 family MPP mode data and probe glue for the shared MVEBU pinctrl core, with variant masks for MV88F6810, MV88F6820, and MV88F6828 capabilities.

## Important APIs, Types, and Data
- Variant bits `V_88F6810`, `V_88F6820`, `V_88F6828`, and combined masks gate functions by SoC model.
- `armada_38x_mpp_modes` describes MPP pins 0-59 with `MPP_VAR_FUNCTION()` entries for GPIO, UART, I2C, GE/MDIO, PCIe, SPI, SATA presence, PTP, DRAM, SD0, device bus, NAND, TDM, audio, and reference clocks.
- `armada_38x_pinctrl_of_match` binds three compatibles and stores the corresponding variant bit in match data.
- `armada_38x_mpp_controls` declares one MMIO control range for pins 0-59.
- `armada_38x_mpp_gpio_ranges` exposes GPIO ranges 0-31 and 32-59.
- `armada_38x_pinctrl_probe()` reads variant match data, fills SoC info, and delegates to `mvebu_pinctrl_simple_mmio_probe()`.

## Control Flow
Probe casts `device_get_match_data()` to the low 8-bit variant mask, populates the shared SoC info structure with controls/ranges/modes, stores it in platform data, and calls the shared simple MMIO probe. The shared core uses the variant mask to expose only valid functions for the matched SoC.

## State and Persistence
This file keeps static mode/control data and a static SoC info structure. MPP selections persist in hardware registers. No local runtime state or suspend/resume code is implemented here.

## Dependencies and Integration Points
It depends on `pinctrl-mvebu.h`, `linux/property.h` for match data access, and OF platform matching. It is selected by `CONFIG_PINCTRL_ARMADA_38X`.

## Risks
Variant masks must be accurate; exposing an unsupported PCIe/SATA/GE function on a lower variant can mislead DT authors and fail hardware operation. Shared-core behavior depends on `soc->nmodes = armada_38x_mpp_controls[0].npins`, so the control range and table length must stay synchronized. Dense table entries for storage/network pins are boot-critical.

## Test Signals
Build and boot each supported compatible (`mv88f6810`, `mv88f6820`, `mv88f6828`), verify variant-filtered functions in debugfs, and test representative UART/I2C/SPI/SD/GE/PCIe/SATA/GPIO paths. Compile-time warnings around pointer-to-integer match-data casts should be watched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-38x.c -->
