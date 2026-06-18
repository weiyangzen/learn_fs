# Research: subset-b-005121

This grouped report covers Linux pinctrl source files under `sources/distributed-fs/ceph-client/drivers/pinctrl/` for the UniPhier, Visconti, and VT8500/WonderMedia families. Each section is bounded for reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pro5.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pro5.c

## Purpose

This file is the Socionext UniPhier Pro5 SoC pinctrl data provider. It supplies the common UniPhier pinctrl core with the Pro5 pin descriptor table, pin groups, pinmux functions, GPIO mux policy, capability flags, OF match table, and platform driver registration for `socionext,uniphier-pro5-pinctrl`.

The file is almost entirely declarative hardware description. Runtime behavior is limited to the SoC-specific GPIO mux value callback, the thin probe wrapper, and builtin platform-driver registration.

## Important APIs, Types, And Data

- `uniphier_pro5_pins[]` is a large `struct pinctrl_pin_desc` array created with `UNIPHIER_PINCTRL_PIN`. Each entry encodes pin number, name, input-enable control, drive-strength control register, drive type, pull register, and pull direction into `drv_data`.
- Group pin arrays cover Pro5 peripheral signals including `emmc`, `emmc_dat8`, I2C controllers `i2c0` through `i2c6` with several `i2c5` alternatives, `nand` plus `nand_cs1`, `pcie`, `sd`, `spi0` to `spi2`, `system_bus` plus chip-select extensions, UART groups including alternate/modem groups, and `usb0` to `usb2`.
- `gpio_range_pins[]` lists sparse pin numbers used to expose GPIO ranges through the common driver.
- `uniphier_pro5_groups[]` maps each named group to its pin list and mux-value list with `UNIPHIER_PINCTRL_GROUP` or GPIO-only group semantics.
- `uniphier_pro5_functions[]` maps Linux pinmux function names to the groups each function may select.
- `uniphier_pro5_get_gpio_muxval()` returns the mux value used when a pin is requested as GPIO.
- `uniphier_pro5_pindata` packages the arrays and callback as `struct uniphier_pinctrl_socdata`.

## Control Flow

At boot or device creation, the builtin platform driver matches `socionext,uniphier-pro5-pinctrl`. `uniphier_pro5_pinctrl_probe()` calls `uniphier_pinctrl_probe(pdev, &uniphier_pro5_pindata)`. The common UniPhier driver then uses the data arrays to register pins, groups, functions, GPIO ranges, pinconf, and pinmux operations.

When a non-GPIO function is selected, the common driver consumes the group descriptor and writes the corresponding mux values for each group pin. When a pin is requested as GPIO, the common driver calls `uniphier_pro5_get_gpio_muxval(pin, gpio_offset)`. Pro5 returns mux value `14` for GPIO offsets `120..141` representing XIRQ lines and `15` otherwise.

## State And Persistence

The file has no mutable module state. Persistent hardware state is the SoC pin controller register state written by the common UniPhier core. All arrays are `static const`, and allocations, locks, and register mappings are owned by the shared driver. The packed per-pin `drv_data` is immutable metadata.

## Dependencies And Integration Points

This file depends on `pinctrl-uniphier.h` for the descriptor macros, `struct uniphier_pinctrl_socdata`, and `uniphier_pinctrl_probe()`. It integrates with the Linux platform bus through `struct platform_driver`, OF matching, and `builtin_platform_driver`. It also depends on the generic Linux pinctrl subsystem indirectly through the common UniPhier driver.

The `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE` flag tells the common driver that debug mux handling is separate on this SoC. GPIO mux semantics are integrated through the `get_gpio_muxval` callback.

## Risks And Edge Cases

- Pin numbering and group pin lists must match the hardware manual and device-tree binding expectations; a wrong entry can silently route a board signal to the wrong function.
- `gpio_range_pins[]` is sparse and must remain aligned with GPIO offset assumptions in `uniphier_pro5_get_gpio_muxval()`.
- XIRQ GPIO offsets use a distinct mux value. Regressions here can break interrupt-capable pins while ordinary GPIO pins still work.
- The descriptor macros perform some compile-time array length checks for group pin/mux arrays, but they cannot validate hardware register offsets or mux values.

## Test Signals

Useful verification signals include successful boot-time probe for `socionext,uniphier-pro5-pinctrl`, absence of pinctrl registration errors, device-tree pinmux selection for eMMC, SD, NAND, SPI, UART, and USB groups, GPIO request tests for normal GPIO and XIRQ offsets, and pinconf validation for drive strength, pull direction, and input-enable behavior through the common UniPhier code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pro5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pxs2.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pxs2.c

## Purpose

This file provides Socionext UniPhier PXs2-specific pinctrl data. It describes the PXs2 pin universe, peripheral groups, pinmux functions, GPIO ranges, SoC GPIO mux callback, and platform driver for `socionext,uniphier-pxs2-pinctrl`.

The file is a hardware-description companion to the common UniPhier pinctrl core. It does not implement generic pinctrl algorithms; it supplies the static data consumed by those algorithms.

## Important APIs, Types, And Data

- `uniphier_pxs2_pins[]` is the PXs2 `struct pinctrl_pin_desc` table, with each pin carrying packed input-enable, drive, pull, and pull-direction metadata through `UNIPHIER_PINCTRL_PIN`.
- Peripheral pin groups include audio input/output groups (`ain1`, `ain2`, `ain3`, `aout1`, `aout2`, `aout3`, IEC pins, and data-width extensions), `emmc`, Ethernet in `ether_mii`, `ether_rgmii`, and `ether_rmii` modes, I2C, NAND with `nand_cs1`, SD, SPI, system bus, UART alternatives, and USB host/device groups.
- `gpio_range0_pins[]` and `gpio_range1_pins[]` describe GPIO exposure ranges for the common driver.
- `uniphier_pxs2_groups[]` binds named groups to pin lists and mux-value arrays.
- `uniphier_pxs2_functions[]` maps functions to one or more groups. Several functions expose alternative groups, such as UART and USB device variants.
- `uniphier_pxs2_get_gpio_muxval()` handles the GPIO mux selection rule for ordinary pins and XIRQ aliases.
- `uniphier_pxs2_pindata` exports all SoC data to `uniphier_pinctrl_probe()`.

## Control Flow

The builtin platform driver matches `socionext,uniphier-pxs2-pinctrl`, then `uniphier_pxs2_pinctrl_probe()` delegates to the common UniPhier probe with `uniphier_pxs2_pindata`.

During normal pinctrl operation, device-tree pinctrl states resolve function names to groups in `uniphier_pxs2_functions[]`, then the common core writes group mux values for the listed pins. GPIO requests flow through `uniphier_pxs2_get_gpio_muxval()`: offsets `120..143`, used for XIRQ aliases, return mux value `14`; all other offsets return `15`.

## State And Persistence

All SoC data in this file is `static const` and immutable. The only persistent state affected by this file is hardware register state written by the common driver using this metadata. There are no file-local locks, allocations, caches, or suspend state.

## Dependencies And Integration Points

This file depends on `pinctrl-uniphier.h` and the common UniPhier driver. It integrates with OF through `socionext,uniphier-pxs2-pinctrl`, with the platform driver core via `builtin_platform_driver`, and with the pinctrl subsystem through the shared `uniphier_pinctrl_probe()` implementation.

Unlike Pro5 and PXs3, `uniphier_pxs2_pindata.caps` is `0`, so the common driver should use baseline UniPhier behavior without separate debug mux or per-pin input-enable capability flags.

## Risks And Edge Cases

- PXs2 includes many alternative and overlapping groups, especially audio, UART, Ethernet, and USB device functions. Incorrect group membership or mux values can break only one alternate mode while leaving others functional.
- The XIRQ GPIO rule relies on GPIO offsets rather than only physical pin numbers; device-tree GPIO ranges must match the callback’s offset assumptions.
- Some groups extend base functions with data-width variants, such as `ain*_dat2`, `ain*_dat4`, `aout*_dat2`, and `aout*_dat4`; missing these in device-tree states can produce partial bus wiring.
- Static compile-time checks catch only pin-array versus mux-array length mismatches, not whether register indices or mux values are electrically valid.

## Test Signals

Validation should include probe against a PXs2-compatible node, device-tree pinmux states for audio, Ethernet MII/RGMII/RMII, eMMC, NAND, SD, UART, USB host/device, and SPI, plus GPIO request tests for ordinary offsets and XIRQ alias offsets. Functional tests should verify wide bus variants such as eMMC DAT8 and audio data-extension groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pxs2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pxs3.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pxs3.c

## Purpose

This file provides the Socionext UniPhier PXs3 pinctrl hardware description. It supplies pin descriptors, pin groups, functions, GPIO range data, a PXs3-specific GPIO mux callback, capability flags, and platform-driver registration for `socionext,uniphier-pxs3-pinctrl`.

The source is data-heavy and is intended to be consumed by the common UniPhier pinctrl implementation.

## Important APIs, Types, And Data

- `uniphier_pxs3_pins[]` enumerates PXs3 pins and packs per-pin electrical controls into `drv_data` with `UNIPHIER_PINCTRL_PIN`.
- Groups cover audio input/output and IEC pins, eMMC with DAT8, two Ethernet controllers with RGMII/RMII choices (`ether_*` and `ether1_*`), I2C, NAND, SD, SPI, system bus, UART with CTS/RTS and modem extras, and USB host/device pins.
- `gpio_range0_pins[]`, `gpio_range1_pins[]`, and `gpio_range2_pins[]` expose sparse GPIO pin ranges.
- `uniphier_pxs3_groups[]` stores the group descriptors, including mux value lists.
- `uniphier_pxs3_functions[]` maps function selectors to group names.
- `uniphier_pxs3_get_gpio_muxval()` contains PXs3’s special XIRQ/GPIO mapping.
- `uniphier_pxs3_pindata` sets `.caps = UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`, indicating per-pin input-enable behavior is available to the common driver.

## Control Flow

The platform driver binds to `socionext,uniphier-pxs3-pinctrl` and calls `uniphier_pinctrl_probe()` with PXs3 data. The common driver registers pinctrl objects and later uses group/function mappings when device-tree pin states are selected.

For GPIO request routing, `uniphier_pxs3_get_gpio_muxval()` returns `0` for XIRQ GPIO offsets `120..143` when the physical pin is in `219..234`, returns `14` for the remaining XIRQ offsets, and returns `15` for ordinary GPIO offsets. This makes PXs3 more nuanced than PXs2 because some XIRQ-capable pins use a GPIO mux value of zero.

## State And Persistence

There is no mutable state in this file. It provides immutable descriptors and callback logic. Hardware register state persists in the pin controller and is manipulated by the common driver during pinmux, GPIO, and pinconf operations.

## Dependencies And Integration Points

The source depends on `pinctrl-uniphier.h` for macros and `struct uniphier_pinctrl_socdata`. It integrates with the Linux platform/OF subsystem through `socionext,uniphier-pxs3-pinctrl` and with generic pinctrl through the shared UniPhier implementation.

The `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL` capability is a key integration signal: the common driver must use per-pin input-enable control rather than a simpler global assumption.

## Risks And Edge Cases

- The special GPIO mux callback has two dimensions, GPIO offset and physical pin number. Bugs in GPIO range tables can produce incorrect muxing even if the callback is unchanged.
- Dual Ethernet controller descriptions and overlapping audio/UART alternatives increase the risk of pin conflicts in board device trees.
- Per-pin input-enable capability means pin descriptor metadata is more important for electrical correctness.
- Mux value tables are static hardware constants; compile-time array-size checks do not prove they match silicon.

## Test Signals

Good test signals are successful probe, selection of both Ethernet controllers in RGMII and RMII modes, eMMC DAT8, SD, NAND, audio, UART CTS/RTS/modem, and USB host/device pin states. GPIO tests should cover normal GPIOs, XIRQ offsets outside pin range `219..234`, and XIRQ offsets on pins `219..234` to verify both special return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pxs3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-sld8.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-sld8.c

## Purpose

This file is the UniPhier SLD8 SoC pinctrl data provider. It describes SLD8 pins, peripheral groups, pinmux functions, sparse GPIO ranges, the SLD8 GPIO mux callback, and the platform driver for `socionext,uniphier-sld8-pinctrl`.

The implementation is declarative data plus a small GPIO mux function and a probe wrapper into the common UniPhier pinctrl driver.

## Important APIs, Types, And Data

- `uniphier_sld8_pins[]` is the SLD8 pin descriptor table with packed pinconf and mux-control metadata.
- Peripheral groups include `emmc` and `emmc_dat8`, Ethernet MII/RMII, I2C0-I2C3, NAND plus `nand_cs1`, SD, SPI0, system bus plus chip-select extensions, UART groups including CTS/RTS and modem, and USB0-USB2.
- `gpio_range0_pins[]`, `gpio_range1_pins[]`, and `gpio_range2_pins[]` define sparse GPIO-exposed pins.
- `uniphier_sld8_groups[]` and `uniphier_sld8_functions[]` provide the group/function mapping consumed by the common driver.
- `uniphier_sld8_get_gpio_muxval()` handles XIRQ GPIO exceptions through a `switch` over GPIO offsets.
- `uniphier_sld8_pindata` packages all arrays and sets baseline capabilities with `.caps = 0`.

## Control Flow

The builtin platform driver binds to `socionext,uniphier-sld8-pinctrl`. Its probe function calls `uniphier_pinctrl_probe()` with `uniphier_sld8_pindata`.

When a device-tree pin state selects a function, the common driver resolves the function to groups and writes the group mux values. GPIO request handling calls `uniphier_sld8_get_gpio_muxval()`, which returns `0` for XIRQ0-XIRQ7 offsets `120..127`, `14` for XIRQ8-XIRQ12 and XIRQ14-XIRQ15 offsets `128..132` and `134..135`, and `15` for other offsets.

## State And Persistence

The source has no mutable state. Register state lives in hardware and is controlled through the shared UniPhier pinctrl implementation. Static arrays in this file are immutable descriptors.

## Dependencies And Integration Points

The file depends on the UniPhier common header and common probe routine. It integrates with OF using `socionext,uniphier-sld8-pinctrl`, registers as a builtin platform driver, and is consumed by generic Linux pinctrl through the common driver.

SLD8 uses baseline UniPhier capabilities and relies on its SoC-specific GPIO mux callback to distinguish XIRQ offset ranges.

## Risks And Edge Cases

- The XIRQ callback intentionally skips offset `133`; this must match hardware and GPIO range definitions.
- Some pins appear in multiple functional contexts, such as I2C and USB/UART alternatives, so board-level pin states must avoid conflicts.
- System bus chip-select groups are split out; missing an extension group can partially configure an external bus.
- As with other UniPhier data files, hardware constants are not validated by the compiler beyond array shape.

## Test Signals

Probe should succeed for an SLD8 device-tree node. Runtime tests should exercise eMMC DAT8, Ethernet MII/RMII, NAND with chip select, SD, SPI0, system bus chip selects, UART modem/CTSRTS, and USB groups. GPIO tests should cover XIRQ offsets in each callback case and an ordinary GPIO offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-sld8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier.h

## Purpose

This header defines the shared data contract between UniPhier SoC-specific pinctrl data files and the common UniPhier pinctrl driver. It provides packed pin-attribute bit layouts, enums for drive and pull behavior, descriptor structs for groups/functions/SoC data, helper macros for declaring pins and groups, and the common probe/PM entry points.

## Important APIs, Types, And Data

- The packed `drv_data` layout stores input-enable control, drive control register, drive type, pull-up/down control register, and pull direction inside an unsigned long. `BUILD_BUG` logic rejects layouts that exceed `BITS_PER_LONG`.
- `enum uniphier_pin_drv_type` describes supported drive-strength models: 1-bit, 2-bit, 3-bit, fixed 4 mA, fixed 5 mA, fixed 8 mA, and no drive support.
- `enum uniphier_pin_pull_dir` describes pull-up, pull-down, fixed pull states, and no pull register.
- `uniphier_pin_get_*()` inline helpers unpack fields from `pinctrl_pin_desc.drv_data`.
- `struct uniphier_pinctrl_group` holds a group name, pins, pin count, and mux value array.
- `struct uniphier_pinmux_function` maps a function name to group names.
- `struct uniphier_pinctrl_socdata` packages SoC descriptors, function/group counts, GPIO mux callback, and capability flags.
- `UNIPHIER_PINCTRL_PIN`, `UNIPHIER_PINCTRL_GROUP`, `UNIPHIER_PINCTRL_GROUP_GPIO`, and `UNIPHIER_PINMUX_FUNCTION` are the main declaration macros used by SoC files.
- `uniphier_pinctrl_probe()` is the shared probe function implemented outside this header; `uniphier_pinctrl_pm_ops` exposes PM hooks.

## Control Flow

SoC files use the macros in this header to create static descriptor tables. Their platform-driver probe wrappers pass a `struct uniphier_pinctrl_socdata` to `uniphier_pinctrl_probe()`. The common driver later unpacks per-pin `drv_data` with the inline helpers when applying pinconf, pinmux, and GPIO operations.

`UNIPHIER_PINCTRL_GROUP` includes a compile-time guard that requires the `grp##_pins` and `grp##_muxvals` arrays to have the same length. GPIO-only groups can use `UNIPHIER_PINCTRL_GROUP_GPIO`, which sets mux values to `NULL`.

## State And Persistence

The header defines no runtime storage by itself. It shapes immutable SoC descriptor data and the interpretation of packed metadata. Persistent state is limited to hardware state manipulated by the common driver using this data.

## Dependencies And Integration Points

The header includes Linux bit/build/kernel/type helpers and forward-declares `struct platform_device`. It integrates with generic pinctrl through `struct pinctrl_pin_desc` users in the SoC data files, with platform drivers through `uniphier_pinctrl_probe()`, and with PM through `uniphier_pinctrl_pm_ops`.

Capability flags currently include `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL` and `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE`, allowing SoC data to select common-driver behavior without changing probe signatures.

## Risks And Edge Cases

- The packed pointer-sized `drv_data` contract is compact but brittle; field width changes must preserve `BITS_PER_LONG` safety on all supported architectures.
- Casts between packed integers and `void *` rely on storing small bitfields in `drv_data`, not actual pointers.
- The compile-time group length check prevents pin/mux count mismatch but cannot validate mux value semantics.
- Adding new drive or pull types requires synchronized changes in the common driver and all data users.

## Test Signals

Compile-time build coverage is important because macro expansion and `BUILD_BUG_ON_ZERO` checks catch descriptor-shape errors. Runtime validation comes indirectly from probing each UniPhier SoC file and applying pinconf for every drive and pull type used in descriptor data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/Kconfig

## Purpose

This Kconfig file defines build-time configuration for Toshiba Visconti pinctrl support. It separates a common Visconti pinctrl core symbol from the TMPV7700 SoC-specific driver symbol.

## Important APIs, Types, And Data

- `PINCTRL_VISCONTI` is a hidden boolean selected by concrete Visconti SoC drivers. It selects `PINMUX`, `GENERIC_PINCONF`, `GENERIC_PINCTRL_GROUPS`, and `GENERIC_PINMUX_FUNCTIONS`.
- `PINCTRL_TMPV7700` is a user-visible boolean for the Toshiba Visconti TMPV7700 series pinctrl driver. It depends on `OF` and on either `ARCH_VISCONTI` or `COMPILE_TEST`, selects `PINCTRL_VISCONTI`, and defaults to `ARCH_VISCONTI`.

## Control Flow

Kconfig resolution occurs at kernel configuration time. Enabling `PINCTRL_TMPV7700` selects the common `PINCTRL_VISCONTI` support, which in turn ensures generic pinctrl, pinmux, and pinconf helpers are available. The Makefile then uses the resolved config symbols to build the common and TMPV7700 objects.

## State And Persistence

The file has no runtime state. Its persistent effect is the generated kernel `.config` and the object inclusion decisions derived from it.

## Dependencies And Integration Points

It integrates with the kernel pinctrl Kconfig hierarchy, architecture selection through `ARCH_VISCONTI`, Open Firmware support through `OF`, and compile coverage through `COMPILE_TEST`.

## Risks And Edge Cases

- Because `PINCTRL_VISCONTI` is hidden, no common object is built unless a concrete SoC driver selects it.
- Missing generic helper selections would cause compile or runtime registration failures in `pinctrl-common.c`; this Kconfig correctly selects the needed generic pinctrl and pinmux/pinconf infrastructure.
- `PINCTRL_TMPV7700` being `bool` means this driver is built in, not modular, when enabled.

## Test Signals

Configuration tests should verify that `ARCH_VISCONTI=y` enables `PINCTRL_TMPV7700` by default and that `COMPILE_TEST=y` on other architectures can build the driver when dependencies are met. Build logs should include both `pinctrl-common.o` and `pinctrl-tmpv7700.o` when TMPV7700 support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/Makefile

## Purpose

This Makefile connects Visconti Kconfig symbols to object files. It builds the common Visconti pinctrl implementation and the TMPV7700 SoC data driver when their symbols are enabled.

## Important APIs, Types, And Data

- `obj-$(CONFIG_PINCTRL_VISCONTI) += pinctrl-common.o` builds the shared implementation.
- `obj-$(CONFIG_PINCTRL_TMPV7700) += pinctrl-tmpv7700.o` builds the TMPV7700 platform driver and descriptor tables.

## Control Flow

During kernel build, Kbuild evaluates these `obj-*` lines after Kconfig resolves symbols. `PINCTRL_TMPV7700` selects `PINCTRL_VISCONTI`, so enabling the concrete driver also includes the common object.

## State And Persistence

The file has no runtime state. It affects build artifacts by determining whether object files are linked into the kernel image.

## Dependencies And Integration Points

The Makefile integrates with the Visconti Kconfig file, Kbuild, and the platform driver implementation split between `pinctrl-common.c` and `pinctrl-tmpv7700.c`.

## Risks And Edge Cases

- If a future SoC selects `PINCTRL_VISCONTI` but omits its own object line, only the common code will build and no matching platform driver will bind.
- If `PINCTRL_TMPV7700` did not select `PINCTRL_VISCONTI`, this Makefile would allow the SoC object to build without the common implementation. Kconfig currently prevents that.

## Test Signals

The expected build signal is that `pinctrl-common.o` appears whenever `CONFIG_PINCTRL_VISCONTI=y`, and both objects appear when `CONFIG_PINCTRL_TMPV7700=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-common.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-common.c

## Purpose

This file implements the shared Toshiba Visconti pinctrl, pinmux, and pinconf logic. SoC-specific files provide descriptor tables and optional unlock hooks; this common file maps MMIO registers, registers the Linux pinctrl device, and implements pin configuration, group lookup, function lookup, mux selection, and GPIO mux enablement.

## Important APIs, Types, And Functions

- `struct visconti_pinctrl` is private runtime state containing MMIO `base`, `dev`, `pctl`, `pctl_desc`, SoC `devdata`, and a spinlock protecting register read-modify-write sequences.
- `visconti_pin_config_set()` supports `PIN_CONFIG_BIAS_PULL_UP`, `PIN_CONFIG_BIAS_PULL_DOWN`, `PIN_CONFIG_BIAS_DISABLE`, and `PIN_CONFIG_DRIVE_STRENGTH`.
- `visconti_pin_config_group_set()` applies the same config list to every pin in a group.
- `visconti_get_groups_count()`, `visconti_get_group_name()`, and `visconti_get_group_pins()` implement `struct pinctrl_ops`.
- `visconti_get_functions_count()`, `visconti_get_function_name()`, `visconti_get_function_groups()`, `visconti_set_mux()`, and `visconti_gpio_request_enable()` implement `struct pinmux_ops`.
- `visconti_pinctrl_probe()` is the exported common probe entry used by SoC-specific platform drivers.

## Control Flow

`visconti_pinctrl_probe()` allocates private state, stores `devdata`, initializes the spinlock, maps the first MMIO resource, copies SoC pin descriptors into a devm-managed `struct pinctrl_pin_desc` array, fills `pctl_desc`, calls `devm_pinctrl_register_and_init()`, runs the optional SoC unlock callback, and finally calls `pinctrl_enable()`.

Pin configuration enters through generic pinconf callbacks. The driver locks, iterates configs, and updates per-pin registers from the SoC descriptor offsets and shifts. Pull-up falls through to pull-down handling after setting the selector bit; pull-up and pull-down both fall through to the enable/disable write. Drive strength accepts 2, 4, 8, 16, 24, and 32 mA and maps those to a 4-bit DSEL code with `DIV_ROUND_CLOSEST(arg, 2) - 1`.

Mux selection locks, reads the group mux register, clears `mux->mask`, ORs `mux->val`, and writes the result. GPIO request enable uses the per-pin `gpio_mux` entry and forces that pin’s mux field to the GPIO value.

## State And Persistence

The private state is devm-managed and lives as long as the platform device. Hardware mux, pull, and drive settings persist in MMIO registers until changed or reset. Register access is serialized by `spin_lock_irqsave()` around each read-modify-write sequence. There is no software persistence across reboot or driver unbind beyond what the pinctrl subsystem and device tree reapply.

## Dependencies And Integration Points

The driver depends on Linux MMIO, platform device, OF, and pinctrl/pinmux/pinconf APIs. It includes pinctrl core internals `../core.h`, generic pinconf helpers, and `pinctrl-utils.h`. SoC-specific data comes through `struct visconti_pinctrl_devdata` from `pinctrl-common.h`.

Device-tree integration uses `pinconf_generic_dt_node_to_map_group`, meaning states are group-oriented. `pinconf_generic_dump_config` provides debug output. `pinmux_ops.strict = true` prevents simultaneous GPIO and mux ownership conflicts.

## Risks And Edge Cases

- `visconti_pin_config_set()` indexes `priv->devdata->pins[_pin]` directly. It assumes pin numbers match dense descriptor indexes; sparse or reordered pin numbers would break.
- Unsupported drive strengths return `-EINVAL`; unsupported config parameters return `-EOPNOTSUPP` and abort the remaining config list.
- Pull configuration intentionally uses fallthrough; missing or misunderstood fallthrough would change behavior.
- `visconti_gpio_request_enable()` indexes `gpio_mux[pin]` directly, also assuming a dense GPIO/pin index space.
- Register offsets, masks, and shifts are trusted SoC data; the common code does not validate overlap or range.

## Test Signals

Unit-level signals are difficult because this is kernel MMIO code. Practical tests include successful probe, pinctrl debugfs showing expected groups/functions, device-tree states applying I2C/SPI/UART/PWM/PCMIF groups, GPIO request ownership respecting strict mode, and pinconf writes for bias disable, pull-up, pull-down, and each accepted drive strength. Negative tests should check invalid drive strengths and unsupported pinconf parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-common.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-common.h

## Purpose

This header defines the shared descriptor ABI between Visconti SoC-specific data files and the Visconti common pinctrl implementation. It provides declaration macros and struct layouts for pins, groups, mux register writes, functions, SoC devdata, and the common probe entry point.

## Important APIs, Types, And Data

- `VISCONTI_PINS()` creates static pin-number arrays for groups.
- `struct visconti_desc_pin` embeds a `struct pinctrl_pin_desc` and stores drive-select offset/shift plus pull-enable, pull-select, and pull-shift metadata.
- `VISCONTI_PIN()` initializes a described pin.
- `VISCONTI_GROUPS()` creates static group-name arrays for functions.
- `struct visconti_mux` stores a mux register offset, bit mask, and value.
- `struct visconti_pin_group` binds a group name, pin list, pin count, and one mux operation.
- `VISCONTI_PIN_GROUP()` derives group names with a `_grp` suffix and fills array size and mux metadata.
- `struct visconti_pin_function` maps function names to group arrays.
- `VISCONTI_PIN_FUNCTION()` creates a function descriptor.
- `struct visconti_pinctrl_devdata` packages pins, groups, functions, GPIO mux table, and optional register unlock callback.
- `visconti_pinctrl_probe()` is the common probe function called by chip drivers.

## Control Flow

SoC files use the macros to declare pin arrays, group arrays, function arrays, and `struct visconti_pinctrl_devdata`. Their probe functions call `visconti_pinctrl_probe()`, which interprets these structures to register pinctrl operations and perform MMIO writes.

The header itself has no active control flow, but its field layout controls how `pinctrl-common.c` calculates register addresses and bit positions for drive, pull, mux, and GPIO selection.

## State And Persistence

The header defines immutable descriptor structures and function pointers only. Runtime state is created in `pinctrl-common.c`; persistent hardware state is MMIO register state.

## Dependencies And Integration Points

It forward-declares `struct pinctrl_pin_desc` and expects Linux pinctrl headers to be included by users. It uses kernel macros such as `ARRAY_SIZE` and `__stringify` through the including translation units. It integrates SoC-specific files like `pinctrl-tmpv7700.c` with the common driver.

## Risks And Edge Cases

- The common driver indexes `pins` and `gpio_mux` by pin number, so descriptors created with these macros should remain dense from zero where needed.
- `VISCONTI_PIN_GROUP()` applies one mux register operation per group; groups requiring multiple discontiguous register updates would need a data model change.
- Group names are mechanically suffixed with `_grp`; function group strings must match that generated naming.
- The optional `unlock` hook must be valid for the SoC register block and run before protected registers need writes.

## Test Signals

Compile tests validate macro expansion and struct initialization. Runtime tests should verify that every function group string corresponds to a generated group name and that every GPIO pin has a matching `gpio_mux` entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-tmpv7700.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-tmpv7700.c

## Purpose

This file provides TMPV7700/TMPV7708-specific data for the Visconti pinctrl common driver. It defines register offsets, pins, groups, functions, GPIO mux entries, the register unlock sequence, and platform-driver binding for `toshiba,tmpv7708-pinctrl`.

## Important APIs, Types, And Data

- Register offset constants describe key/unlock registers, five pinmux registers, IO select/voltage/drive registers, and pull-enable/pull-select registers.
- `pins_tmpv7700[]` describes 35 pins: GPIO0-GPIO31 plus SPI pins `spi_sck`, `spi_sdo`, and `spi_sdi`. Each pin includes DSEL and PUDE/PUDSEL offsets and shifts.
- Group pin arrays cover I2C0-I2C8, SPI0-SPI6 with chip selects, UART0-UART3, PWM alternatives on GPIO4-GPIO19, and PCMIF input/output.
- `groups_tmpv7700[]` maps each group to a register offset, mask, and mux value.
- `functions_tmpv7700[]` exposes pinmux functions for I2C, SPI, UART, PWM, and PCMIF.
- `gpio_mux_tmpv7700[]` provides one GPIO mux operation per GPIO-capable pin, mostly clearing four-bit fields in `REG_PINMUX2` through `REG_PINMUX5`.
- `tmpv7700_pinctrl_unlock()` writes `1` to `REG_KEY_CTRL` and `tmpv7700_MAGIC_NUM` to `REG_KEY_CMD`.
- `tmpv7700_pinctrl_data` packages data for `visconti_pinctrl_probe()`.

## Control Flow

The platform driver registers at `arch_initcall()` and matches `toshiba,tmpv7708-pinctrl`. `tmpv7700_pinctrl_probe()` delegates to the common Visconti probe with `tmpv7700_pinctrl_data`. The common probe maps registers, registers the pinctrl device, invokes `tmpv7700_pinctrl_unlock()`, and enables pinctrl.

At runtime, function selection uses `groups_tmpv7700[]` register masks and values. GPIO request enable uses `gpio_mux_tmpv7700[]` to clear a pin’s mux field to GPIO mode. Pinconf uses the per-pin DSEL and pull offsets from `pins_tmpv7700[]`.

## State And Persistence

This file contains only static descriptor data and an unlock write sequence. Hardware state persists in the TMPV7700 pinmux and IO registers. The common driver owns private state, locking, and MMIO access.

## Dependencies And Integration Points

It depends on `pinctrl-common.h`, Linux platform/OF APIs, and the common Visconti implementation. It integrates with device trees that use `toshiba,tmpv7708-pinctrl`. Build inclusion is controlled by `CONFIG_PINCTRL_TMPV7700`.

The data model assumes the common driver can represent each functional group with a single register offset/mask/value tuple, which is true for the listed TMPV7700 groups.

## Risks And Edge Cases

- Register unlock must occur before protected pinmux writes are needed; the common probe calls unlock after registration and before `pinctrl_enable()`.
- `gpio_mux_tmpv7700[]` has 32 entries while `pins_tmpv7700[]` has 35 pins. The common GPIO path indexes by pin, so GPIO requests for the SPI-only pins would be unsafe unless those pins are never requested as GPIO.
- Many functions share the same physical pins with different four-bit mux values, such as PWM and UART/SPI alternatives; board device-tree states must avoid conflicts.
- The common driver assumes dense pin numbering from zero; TMPV7700 satisfies this with pins 0 through 34.

## Test Signals

Verify probe and unlock on TMPV7708 hardware or emulation, pinctrl debugfs function/group listings, GPIO requests for GPIO0-GPIO31, and pinmux selection for I2C0-I2C8, SPI0-SPI6 including chip selects, UART0-UART3, PWM alternatives, and PCMIF. Pinconf tests should cover pull-up/down/disable and supported drive strengths on several DSEL registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-tmpv7700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/Kconfig

## Purpose

This Kconfig file defines pinctrl support options for VIA/WonderMedia VT8500-family SoCs. It has a hidden common support symbol and user-visible SoC-specific booleans for VT8500, WM8505, WM8650, WM8750, and WM8850.

## Important APIs, Types, And Data

- `PINCTRL_WMT` is a hidden common boolean selected by every concrete WMT-family driver. It selects `PINMUX` and `GENERIC_PINCONF`.
- `PINCTRL_VT8500` depends on `ARCH_WM8505` and supports VIA VT8500.
- `PINCTRL_WM8505` and `PINCTRL_WM8650` depend on `ARCH_WM8505`.
- `PINCTRL_WM8750` depends on `ARCH_WM8750`.
- `PINCTRL_WM8850` depends on `ARCH_WM8850`.
- The whole block is gated by `if ARCH_VT8500`.

## Control Flow

Configuration resolves under the `ARCH_VT8500` architecture family. Selecting any concrete SoC driver selects the common `PINCTRL_WMT` symbol. The Makefile then builds `pinctrl-wmt.o` and the selected SoC data object.

## State And Persistence

The file has no runtime state. Its persistence is the generated kernel config and resulting linked objects.

## Dependencies And Integration Points

It integrates with architecture Kconfig symbols, the generic pinmux and pinconf subsystems, and the vt8500 Makefile. Concrete drivers are `bool`, so enabled support is built in.

## Risks And Edge Cases

- `PINCTRL_VT8500` depending on `ARCH_WM8505` looks historically tied to the architecture family naming; changing architecture symbols could accidentally hide VT8500 support.
- Because all options are inside `if ARCH_VT8500`, `COMPILE_TEST` does not appear to expose these drivers on unrelated architectures.
- The common symbol must stay selected by every concrete driver or the SoC object will lack its shared implementation.

## Test Signals

Kconfig tests should verify visibility under each architecture symbol and that selecting a SoC driver selects `PINCTRL_WMT`. Build logs should show `pinctrl-wmt.o` plus the chosen SoC object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/Makefile

## Purpose

This Makefile maps VT8500/WonderMedia pinctrl configuration symbols to Kbuild object files. It ensures the shared WMT pinctrl core and selected SoC descriptor drivers are compiled.

## Important APIs, Types, And Data

- `obj-$(CONFIG_PINCTRL_WMT) += pinctrl-wmt.o` builds the common core.
- SoC objects are selected by `CONFIG_PINCTRL_VT8500`, `CONFIG_PINCTRL_WM8505`, `CONFIG_PINCTRL_WM8650`, `CONFIG_PINCTRL_WM8750`, and `CONFIG_PINCTRL_WM8850`.

## Control Flow

After Kconfig selection, Kbuild includes object files whose config symbol is `y`. Each SoC option selects `PINCTRL_WMT`, so the shared implementation should be linked with any concrete SoC file.

## State And Persistence

There is no runtime state. The file controls build output and linking.

## Dependencies And Integration Points

It integrates with `vt8500/Kconfig`, the common `pinctrl-wmt.c` implementation, and SoC data files that call `wmt_pinctrl_probe()`.

## Risks And Edge Cases

- Adding a new SoC Kconfig option requires a matching Makefile object line and a selection of `PINCTRL_WMT`.
- Building multiple concrete SoC drivers into one kernel is supported by distinct object files, but they all rely on the shared common object.

## Test Signals

Build with each SoC config enabled and verify the common object and selected SoC object are present. Multi-SoC builds should link without duplicate symbol conflicts because each file uses static driver structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-vt8500.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-vt8500.c

## Purpose

This file supplies VIA VT8500 SoC-specific data to the shared WonderMedia/VIA `pinctrl-wmt` driver. It defines GPIO bank register offsets, symbolic pin IDs, pin descriptors, one-pin group names, and the platform driver for `via,vt8500-pinctrl`.

## Important APIs, Types, And Data

- `vt8500_banks[]` describes seven WMT GPIO banks with enable, direction, data-out, data-in, pull-enable, and pull-config register offsets. Pull registers are `NO_REG` for all banks.
- `WMT_PIN_*` macros map bank/bit pairs to packed pin IDs with `WMT_PIN(bank, bit)`.
- `vt8500_pins[]` enumerates external GPIOs, UARTs, SPI, SD/MMC/MS, I2C, MII Ethernet, serial EEPROM, IDE, video in/out, NAND control, transport stream, and LCD pins.
- `vt8500_groups[]` is a name array matching `vt8500_pins[]` order; each group is effectively one pin for the common WMT model.
- `vt8500_pinctrl_probe()` allocates `struct wmt_pinctrl_data`, fills bank/pin/group counts and pointers, and calls `wmt_pinctrl_probe()`.

## Control Flow

The builtin platform driver binds to `via,vt8500-pinctrl`. Probe allocates devm-managed `wmt_pinctrl_data`, assigns static arrays, and delegates to the common WMT probe. Runtime pinctrl operations are implemented by `pinctrl-wmt.c`, which uses bank offsets to manipulate GPIO enable, direction, input, output, and pinconf registers.

## State And Persistence

This file has no mutable state after probe allocation. The `wmt_pinctrl_data` instance is devm-managed by the platform device. Hardware register state is persisted in the GPIO/pinctrl register block until changed or reset.

## Dependencies And Integration Points

The source depends on `pinctrl-wmt.h`, Linux platform driver APIs, and the common WMT implementation. It integrates with OF through `via,vt8500-pinctrl` and with Kconfig through `CONFIG_PINCTRL_VT8500`.

The comment warns not to reorder banks because bank ordering defines stable Linux pin numbering, especially dedicated external GPIOs in bank 0.

## Risks And Edge Cases

- Reordering bank descriptors or pin arrays changes ABI-visible pin numbers.
- Bank 0 has `NO_REG` for enable, marking dedicated GPIO behavior in the common core; incorrect `NO_REG` usage changes mux/GPIO semantics.
- Pull registers are unavailable for all VT8500 banks, so generic pull configuration should be unsupported or ignored by the common driver.
- The group array must remain in exactly the same order as `vt8500_pins[]`.

## Test Signals

Probe should succeed for `via,vt8500-pinctrl`. GPIO tests should cover dedicated external GPIO bank 0 and non-dedicated banks. Pinctrl debugfs should list the same number of pins and groups. Board tests should exercise UART, SPI, SD/MMC, I2C, MII, LCD, video, IDE, and NAND pins where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-vt8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8505.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8505.c

## Purpose

This file provides WonderMedia WM8505-specific pinctrl data for the shared `pinctrl-wmt` driver. It defines bank register layouts, pin IDs, pin descriptors, matching group names, and the platform driver for `wm,wm8505-pinctrl`.

## Important APIs, Types, And Data

- `wm8505_banks[]` describes eleven banks. All banks have enable, direction, data-out, and data-in registers; pull-enable and pull-config are `NO_REG`.
- Pin macros and `wm8505_pins[]` enumerate external GPIOs, wake/suspend GPIOs, SD/MMC, video input/output and syncs, NOR data/address bus, AC97, serial flash, SPI0-SPI2, UART0-UART3, and I2C0-I2C2.
- `wm8505_groups[]` mirrors `wm8505_pins[]` by name and order, preserving the common WMT one-pin group model.
- `wm8505_pinctrl_probe()` allocates `wmt_pinctrl_data`, fills static descriptors, and calls `wmt_pinctrl_probe()`.

## Control Flow

The builtin platform driver matches `wm,wm8505-pinctrl`. Probe initializes the common driver data from static arrays and delegates all real pinctrl/GPIO/pinconf behavior to `pinctrl-wmt.c`.

Runtime operations use the bank register offsets to switch mux/GPIO enable, direction, and data bits. Since pull registers are absent, pull configuration support depends on the common driver returning unsupported behavior for those banks.

## State And Persistence

All SoC descriptions are static. The only runtime allocation is the devm-managed `wmt_pinctrl_data` created in probe. Persistent hardware state is register state in the GPIO memory space.

## Dependencies And Integration Points

The file depends on `pinctrl-wmt.h`, `wmt_pinctrl_probe()`, Linux platform APIs, and OF matching through `wm,wm8505-pinctrl`. Kconfig symbol `CONFIG_PINCTRL_WM8505` controls build inclusion.

## Risks And Edge Cases

- The code explicitly says dedicated external GPIOs should remain in bank 0 and banks must not be reordered; this is a Linux pin-numbering ABI risk.
- `wm8505_groups[]` must stay aligned with `wm8505_pins[]`.
- Pull configuration registers are not present, so device-tree states requiring pulls may fail or have no effect.
- The bank 9 data-in offset duplicates bank 0's `0xDC` value in the descriptor table, which may be intentional hardware mapping but is a high-value item to verify against the manual.

## Test Signals

Expected signals include successful probe, matching pin/group counts, GPIO operations on external GPIO and higher banks, and board-level pin use for SD/MMC, NOR, AC97, serial flash, SPI, UART, I2C, and video outputs. Negative pinconf tests should cover pull settings on `NO_REG` pull banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8505.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8650.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8650.c

## Purpose

This file supplies WonderMedia WM8650 pinctrl data to the common WMT driver. It describes eight GPIO banks with pull support, pin IDs, pin descriptors, one-pin groups, and the platform driver for `wm,wm8650-pinctrl`.

## Important APIs, Types, And Data

- `wm8650_banks[]` defines eight banks with enable, direction, data-out, data-in, pull-enable, and pull-config registers.
- `wm8650_pins[]` includes external GPIOs, wake/suspend GPIOs, SD card-detect pins, 24-bit video output, video input, I2C, SPI0, SD0/SD1 buses, UART0-UART3, keypad rows/columns, and SD1 control pins.
- `wm8650_groups[]` mirrors the pin descriptor names in order.
- `wm8650_pinctrl_probe()` allocates and populates `wmt_pinctrl_data` before calling the shared WMT probe.

## Control Flow

The builtin platform driver binds to `wm,wm8650-pinctrl` and delegates to `wmt_pinctrl_probe()`. The common driver interprets bank offsets and one-pin groups for GPIO, pinmux, and generic pinconf operations.

Because pull-enable and pull-config registers are present for all banks, generic pull configuration has real hardware-backed state on this SoC.

## State And Persistence

The source’s static arrays are immutable. Probe-created `wmt_pinctrl_data` is devm-managed. Hardware state persists in bank registers, including pull-enable and pull-config state.

## Dependencies And Integration Points

It depends on `pinctrl-wmt.h`, the common WMT driver, platform/OF APIs, and `CONFIG_PINCTRL_WM8650`. The OF compatible is `wm,wm8650-pinctrl`.

## Risks And Edge Cases

- Bank order and pin order are ABI-sensitive.
- Pull register support means incorrect pull offsets affect electrical behavior directly, unlike older no-pull variants.
- The pin set has multiple SD buses and SD card-detect/write-protect pins; board device trees must select the intended bus and avoid conflicts.
- Group names must remain aligned with pin descriptor order.

## Test Signals

Probe and pin/group count should match. GPIO tests should exercise several banks and pull configuration. Board-level smoke tests should cover video, I2C, SPI0, SD0/SD1, UARTs, keypad, and card-detect/write-protect pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8750.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8750.c

## Purpose

This file provides WonderMedia WM8750-specific descriptor data for the shared WMT pinctrl driver. It defines eleven banks, pin descriptors, group names, and the builtin platform driver for `wm,wm8750-pinctrl`.

## Important APIs, Types, And Data

- `wm8750_banks[]` describes eleven banks with enable, direction, data-out, data-in, pull-enable, and pull-config register offsets.
- `wm8750_pins[]` covers external GPIOs, wake pins, SD0 card detect, 24-bit video output, video input, SPI0 with multiple chip-selects, SD0/SD1/SD2 buses and control pins, I2C0-I2C2, UART0-UART3, PWM outputs, and SD power/write-protect/card-detect pins.
- `wm8750_groups[]` mirrors pin names in descriptor order.
- `wm8750_pinctrl_probe()` allocates `wmt_pinctrl_data`, assigns static descriptors, and calls the common WMT probe.

## Control Flow

The platform driver binds to `wm,wm8750-pinctrl`. Probe delegates to the common driver, which uses bank offsets and pin/group arrays to implement pinctrl, pinmux, GPIO, and pinconf operations.

## State And Persistence

Static arrays are immutable. Runtime state is held by the common driver through a devm-managed `wmt_pinctrl_data`. Hardware state persists in GPIO/pinctrl registers, including pull registers.

## Dependencies And Integration Points

The file depends on `pinctrl-wmt.h`, the common WMT implementation, Linux platform APIs, and OF. It is built by `CONFIG_PINCTRL_WM8750` and matches `wm,wm8750-pinctrl`.

## Risks And Edge Cases

- Bank and pin ordering must not change because it changes Linux pin numbering.
- WM8750 has three SD interfaces plus SPI chip-select alternatives and PWM outputs; pin conflicts are likely if device-tree states are not carefully composed.
- The group list must remain order-aligned with `wm8750_pins[]`.
- Pull support makes register offset accuracy important for board-level signal integrity.

## Test Signals

Probe should expose matching pin/group counts. GPIO and pinconf tests should cover pull-enabled banks. Board smoke tests should exercise SPI0, SD0/SD1/SD2 including power and card-detect lines, I2C, UART, PWM, and video pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8850.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8850.c

## Purpose

This file provides WonderMedia WM8850 SoC pinctrl data for the common WMT driver. It defines bank registers, pin descriptors, one-pin group names, and the platform driver for `wm,wm8850-pinctrl`.

## Important APIs, Types, And Data

- `wm8850_banks[]` uses the same eleven-bank register layout pattern as WM8750, including pull-enable and pull-config registers.
- `wm8850_pins[]` describes external GPIOs, wakeup and suspend GPIOs, SD0 card detect, video output/input, SPI0, SD0/SD1/SD2 controls, I2C0-I2C2, UART0-UART2, PWM outputs, and SD power/write-protect/card-detect pins.
- `wm8850_groups[]` mirrors the pin descriptors in order for the one-pin group model.
- `wm8850_pinctrl_probe()` allocates `wmt_pinctrl_data`, fills bank/pin/group fields, and calls `wmt_pinctrl_probe()`.

## Control Flow

The builtin platform driver matches `wm,wm8850-pinctrl`. Probe initializes shared WMT data and delegates all operations to the common driver. The common driver handles GPIO direction/data, muxing, and generic pinconf based on the bank offsets and group names.

## State And Persistence

This file provides immutable descriptors only. Runtime data is devm-managed in the common driver. Hardware pin state persists in MMIO registers.

## Dependencies And Integration Points

It depends on `pinctrl-wmt.h`, common WMT logic, Linux platform/OF APIs, and `CONFIG_PINCTRL_WM8850`. It uses OF compatible `wm,wm8850-pinctrl`.

## Risks And Edge Cases

- WM8850 is similar to WM8750 but has a reduced UART/SD2 pin set; copying assumptions from WM8750 could expose nonexistent pins.
- Bank and group order are ABI-sensitive.
- Pull register offsets must match hardware because generic pinconf can alter electrical behavior.
- Group names must stay aligned with pin descriptors for common WMT lookup.

## Test Signals

Probe should expose the expected number of pins and groups. Runtime tests should exercise GPIO, pull configuration, video pins, SPI0, SD0/SD1/SD2 controls present on WM8850, I2C, UART0-UART2, PWM, and wake/suspend GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8850.c -->
