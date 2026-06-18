# subset-b-005088 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1315e.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1315e.c

## Purpose
Defines the SoC-specific pin controller description for the Realtek RTD1315E ISO pin bank. The file does not implement pinctrl algorithms itself; it enumerates RTD1315E pins, groups, functions, mux register fields, electrical configuration fields, and special drive-strength subfields, then registers a platform driver that passes this static descriptor to the shared Realtek DHC pinctrl core in `pinctrl-rtd.c`.

## Important APIs, Types, and Functions
The central data exported to the common core is `rtd1315e_iso_pinctrl_desc`, a `struct rtd_pinctrl_desc` containing `rtd1315e_iso_pins`, `rtd1315e_pin_groups`, `rtd1315e_pin_functions`, `rtd1315e_iso_muxes`, `rtd1315e_iso_configs`, and `rtd1315e_iso_sconfigs`. `enum rtd13xxe_iso_pins` assigns stable pin numbers for GPIOs, eMMC pins, USB CC pins, HIF pins, UART0 pins, selector pseudo-pins, reset/test pins, and dummy holes. `DECLARE_RTD1315E_PIN`, `RTD1315E_GROUP`, and `RTD1315E_FUNC` generate the one-pin group arrays, group descriptors, and function descriptors consumed by pinctrl.

The platform entry points are `rtd1315e_pinctrl_probe`, `rtd1315e_pinctrl_init`, and `rtd1315e_pinctrl_exit`. Device-tree matching is via `realtek,rtd1315e-pinctrl`, and `MODULE_DEVICE_TABLE(of, rtd1315e_pinctrl_of_match)` supports module alias generation.

## Control Flow
At `arch_initcall` time, `rtd1315e_pinctrl_init()` registers `rtd1315e_pinctrl_driver`. When a DT platform device with the matching compatible probes, `rtd1315e_pinctrl_probe()` calls `rtd_pinctrl_probe(pdev, &rtd1315e_iso_pinctrl_desc)`. The shared core maps the MMIO resource, creates a regmap, registers a `pinctrl_dev`, and uses the descriptor for pinctrl, pinmux, and pinconf callbacks.

At runtime, a function selection request resolves from function selector to a function name, then to one or more group names, then to one or more pin numbers. For each pin, the common core indexes `rtd1315e_iso_muxes[pin]`, searches the per-pin `RTK_PIN_FUNC()` table for the requested function name, and updates the mux register field with `regmap_update_bits()`. GPIO requests use the same path with function name `"gpio"`. Pin configuration requests index `rtd1315e_iso_configs[pin]` and update pull, Schmitt, drive-strength, and power-source bits according to the generic pinconf parameter.

## State and Persistence Behavior
This file is static configuration only. It owns no dynamic state, workqueues, IRQs, locks, or persistent storage. Runtime state is in the common `struct rtd_pinctrl`: MMIO base, regmap, registered pinctrl device, and descriptor pointer. Register writes persist in the SoC pinctrl hardware until reset or power-state loss. The descriptor does not set `.pin_range`, and the platform driver does not attach `realtek_pinctrl_pm_ops`, so this RTD1315E driver does not request the shared suspend/resume register save/restore path.

## Dependencies and Integration Points
The driver depends on Linux platform-device, OF matching, module metadata, pinctrl core types, and `pinctrl-rtd.h` macros. Kconfig builds it under `CONFIG_PINCTRL_RTD1315E`, which depends on the shared `CONFIG_PINCTRL_RTD` core. Integration with other subsystems is through pinctrl DT states and GPIO pin requests: eMMC/NF, UART0/1/2, GSPI, I2C, PCIe, Ethernet LED/PHY, SPI, PWM, SPDIF, USB Type-C CC, SD/HIF, audio/DMIC/TDM/VTC, EJTAG, debug, and boot/test functions are all represented as pinctrl function names.

## Risks
The mux and config arrays are indexed directly by enum pin number, so enum order, holes, dummy pins, and `ARRAY_SIZE()` relationships are ABI-like within the driver. Sparse entries intentionally leave unsupported pins with `.name == NULL`; changing the enum or adding pins without matching mux/config entries can silently make a pin unsupported or point at the wrong register field. Function and group names must match exactly across `rtd1315e_pin_functions`, group arrays, and each `RTK_PIN_FUNC()` entry, because the common core compares strings at mux time.

Electrical configuration values are register-bit descriptions, not policy. Incorrect base bits, offsets, current type (`PADDRI_4_8`, `PADDRI_2_4`, or `NA`), or sconfig masks can produce invalid bias, drive, duty-cycle, or power-source programming. The file uses the base `RTK_PIN_CONFIG` macro, so newer shared-core fields such as input-voltage, slew-rate, and high-VIL are not deliberately described here. Debug, EJTAG, boot, reset, watchdog-reset, and test-mode selector pins are high-risk because exposing or misrouting them can alter board bring-up and debug behavior.

## Test Signals
Build coverage should include `CONFIG_PINCTRL_RTD=y/m` and `CONFIG_PINCTRL_RTD1315E=y/m`. Probe signals include DT binding with `compatible = "realtek,rtd1315e-pinctrl"`, successful MMIO resource mapping, regmap creation, and pinctrl registration. Runtime validation should exercise representative mux states for eMMC/NF, UART0, UART2 loc0/loc1 plus disable selector, GSPI loc0/loc1 plus disable selector, I2C0/1/4/5, SD/HIF, SPI, PWM loc variants, SPDIF loc variants, USB CC pins, audio/DMIC/VTC selectors, and EJTAG disable/location selectors. Pinconf tests should cover pull up/down/disable, Schmitt, 4/8 mA drive selection, power-source bits on eMMC/HIF-style pins, and custom P/N drive and duty-cycle sconfigs. Negative tests should request unsupported functions and unsupported pin configs and expect `-EINVAL` or `-ENOTSUPP` from the shared core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1315e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1319d.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1319d.c

## Purpose
Provides the Realtek RTD1319D ISO pin bank description for the shared Realtek DHC pinctrl core. It maps RTD1319D package pins and selector pseudo-pins to Linux pinctrl groups, functions, mux register fields, pin configuration fields, and special drive-strength fields, then registers a small platform driver for `realtek,rtd1319d-pinctrl`.

## Important APIs, Types, and Functions
`enum rtd13xxd_iso_pins` defines the pin-number namespace, including GPIO0-64, USB CC pins, HIF pins, UART0 pins, eMMC pins, selector pins for UART2/GSPI/HI/SF/EJTAG/DMIC/VTC/audio/SPDIF/HIF/smart-card routing, and boot/reset/test pins. `rtd1319d_iso_pins` exposes those names to the kernel pinctrl framework. `rtd1319d_pin_groups` is generated from one-pin arrays using `DECLARE_RTD1319D_PIN` and `RTD1319D_GROUP`.

`rtd1319d_pin_functions` is the function catalog. It includes baseline GPIO/NF/eMMC plus RTD1319D-specific routes for transport-stream pins (`tp0`, `tp1`), smart-card interfaces (`sc0`, `sc1`, and data selectors), AO pins, GSPI, UARTs, I2C0/1/3/4/5, PCIe1, SDIO, Ethernet LED/PHY, SPI, PWM loc variants, QAM AGC, SPDIF loc variants, VFD, SD/HIF, DMIC/audio/VTC, DC fan, PLL test, EJTAG for SCPU/ACPU/VCPU/SECPU/AUCPU, debug outputs, standby debug, and PMIC power-up. The descriptor `rtd1319d_iso_pinctrl_desc` passes all tables to `rtd_pinctrl_probe()`.

## Control Flow
`rtd1319d_pinctrl_init()` registers a platform driver at `arch_initcall`. On DT match, `rtd1319d_pinctrl_probe()` delegates to the shared Realtek probe. The common core uses `rtd1319d_iso_pinctrl_desc` to publish groups and functions, and later services mux/config requests by direct pin-number indexing into `rtd1319d_iso_muxes` and `rtd1319d_iso_configs`.

Mux control is declarative: each populated `RTK_PIN_MUX()` entry names a pin, gives a mux register offset and mask, and lists accepted function-name/value pairs. Selector pseudo-pins such as `ur2_loc`, `gspi_loc`, `spdif_loc`, `sc0_loc`, and `sc1_loc` are modeled as pinctrl groups too, so selecting a routed function can program both the data pins and the selector field. Pinconf control is similarly declarative through `RTK_PIN_CONFIG()` and `RTK_PIN_SCONFIG()` entries for bias, Schmitt, coarse drive strength, power source, and custom P/N drive and duty-cycle fields.

## State and Persistence Behavior
The file contains only constant tables plus platform-driver registration. It does not allocate state, persist data outside hardware registers, or implement suspend/resume logic. Runtime MMIO and regmap state are owned by the shared core. `rtd1319d_iso_pinctrl_desc` does not provide `.pin_range`, and the platform driver has no `.pm` pointer, so the common save/restore implementation is not active for this variant.

## Dependencies and Integration Points
The file depends on `pinctrl-rtd.h`, Linux pinctrl descriptors, platform drivers, OF matching, and module alias support. It is built by `CONFIG_PINCTRL_RTD1319D`, which depends on `CONFIG_PINCTRL_RTD`. Board integration occurs through DT pinctrl states that use the function and group names from this file. The driver is an integration point for storage (eMMC/NF/SD/SDIO/SPI), low-speed serial (UART/I2C/GSPI/smart-card), networking pins, audio pins, USB Type-C CC pins, PCIe, debug/JTAG, and board-control pins.

## Risks
The descriptor relies on dense-enough enum values matching sparse static arrays. Any pin-number reorder or missing designated initializer can redirect mux/config writes to the wrong register description. Group and function names are string-coupled; misspellings between function group arrays and per-pin `RTK_PIN_FUNC()` entries produce runtime mux failures only when a DT state or GPIO request tries that path.

Some entries deliberately model route selectors as pseudo-pins rather than package pins. Those selectors can be easy to omit from a DT pinctrl state: for example, smart-card data, UART2 location, GSPI location, SPDIF location, and EJTAG target location often require programming both data pins and selector fields. `RTD1319D_ISO_GPIO_DUMMY_77` appears in the pin list as `"dummy"` but is not declared as a group, which is intentional but makes pin-count and enum maintenance more fragile. `rtd1319d_iso_muxes` ends with an explicit zero entry for `TESTMODE`; unsupported muxes return success without programming when the common core sees no mux name, so missing table coverage can be silent for GPIO requests.

## Test Signals
Compile and module-alias checks should cover `CONFIG_PINCTRL_RTD1319D` and the `realtek,rtd1319d-pinctrl` compatible. Probe tests should verify MMIO resource mapping and pinctrl registration. Functional tests should exercise eMMC/NF, GPIO fallback, UART0/1/2 with selector disable/loc0/loc1, GSPI selector paths, I2C0/1/3/4/5, SDIO, SD/HIF, smart-card SC0/SC1 data selectors, SPI, PWM loc variants, QAM AGC, VFD, SPDIF loc variants, USB CC, audio/DMIC/VTC selectors, and each EJTAG disable/location selector including SECPU. Pinconf tests should cover both simple GPIO-style 4/8 mA pins and eMMC/HIF/SDIO-style sconfig pins. Negative tests should intentionally request unsupported pin configs, unsupported function names, and selector-less routed functions to confirm errors or observable misrouting in debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1319d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1619b.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1619b.c

## Purpose
Defines the Realtek RTD1619B ISO pin controller tables for the shared Realtek DHC pinctrl driver. Compared with the RTD13xx variants, this SoC description has wider mux fields on many pins, explicit SPI flash pins, NF-SPI and eMMC-SPI alternatives, SDIO/HI location selectors, PWM open-drain selector pseudo-pins, and multiple EJTAG target selectors.

## Important APIs, Types, and Functions
`enum rtd16xxb_iso_pins` is the pin-number contract for GPIO0-76, USB CC pins, HIF pins, UART0 pins, eMMC pins, SPI flash pins, and selector pseudo-pins for UART2, GSPI, SDIO, HI, HI width, serial flash, ARM trace debug, PWM open-drain modes, EJTAG, DMIC, ISO GSPI, VE3 EJTAG, and AUCPU0/AUCPU1 EJTAG. `rtd1619b_iso_pins` maps those numbers to pin names.

`rtd1619b_pin_groups` is composed of one-pin groups generated by `DECLARE_RTD1619B_PIN` and `RTD1619B_GROUP`. `rtd1619b_pin_functions` catalogs GPIO, NF, NF-SPI, SPI, PMIC, SPDIF/coaxial/optical routes, eMMC-SPI, eMMC, smart-card, UART, GSPI and ISO-GSPI, I2C, PWM, Ethernet, VFD, PCIe1/2, SD, SDIO locations, HI, audio/DMIC/TDM/VTC, transport-stream, AO, selector disable states, EJTAG target/location states, serial-flash enable, ARM trace enable, PWM normal/open-drain, standby debug, USB CC, IR, and test-loop disable functions. `rtd1619b_iso_muxes`, `rtd1619b_iso_configs`, and `rtd1619b_iso_sconfigs` define mux and electrical register fields. `rtd1619b_pinctrl_probe()` passes `rtd1619b_iso_pinctrl_desc` to `rtd_pinctrl_probe()`.

## Control Flow
The driver registers at `arch_initcall` through `rtd1619b_pinctrl_init()`. When a matching `realtek,rtd1619b-pinctrl` platform device probes, all behavioral work moves into the shared Realtek pinctrl core. Group/function enumeration comes from the static descriptor. Function selection updates each selected pin's mux field by matching the requested function name against the pin's `RTK_PIN_FUNC()` list. GPIO request enable selects `"gpio"` where a GPIO mux value exists.

Route selectors are modeled as pinctrl groups, so location functions such as `uart2_loc0`, `uart2_loc1`, `gspi_loc0`, `iso_gspi_loc1`, `sdio_loc0`, `hi_loc0`, and EJTAG loc variants can include both package pins and selector pseudo-pins in the function's group list. Electrical configuration follows the common `rtd_pconf_parse_conf()` path, using register offset/base-bit descriptions from `rtd1619b_iso_configs` and special P/N drive and duty-cycle masks from `rtd1619b_iso_sconfigs`.

## State and Persistence Behavior
This file owns no mutable state beyond platform-driver registration. Hardware mux and pinconf register values persist only in the pinctrl register block. The shared `struct rtd_pinctrl` stores the mapped base, regmap, `pinctrl_dev`, and descriptor pointer. `rtd1619b_iso_pinctrl_desc` does not include a register `pin_range`, and the platform driver does not set `.pm = &realtek_pinctrl_pm_ops`, so common NOIRQ suspend/resume save/restore support is not enabled by this file.

## Dependencies and Integration Points
The file depends on Linux module, OF, platform-device, pinctrl, and the local `pinctrl-rtd.h` macros. Kconfig builds it under `CONFIG_PINCTRL_RTD1619B`, depending on the common Realtek DHC pinctrl core. It integrates with DT pinctrl consumers across storage, boot flash, PMIC SPI, UART, I2C, GSPI/ISO-GSPI, SD/SDIO/HIF, PCIe, Ethernet, VFD, PWM, fan, USB CC, IR, smart-card, audio, transport-stream, AO, debug/JTAG, and trace functions.

## Risks
RTD1619B uses many nonuniform mux masks, including 1-bit, 2-bit, 3-bit, 4-bit, and 5-bit fields. Several `RTK_PIN_FUNC()` values use large encoded values such as `0x10`, `0x11`, and later target selectors shifted into those wider fields. A wrong mask width or shifted value can corrupt neighboring mux fields or make a function unreachable. Unlike the RTD1315E and RTD1319D drivers, this file does not call `MODULE_DEVICE_TABLE(of, rtd1619b_pinctrl_of_match)`, so module autoload by DT alias may be weaker if built as a module.

Function-name coupling is extensive. The same physical pins participate in overlapping routes such as NF, SPI, NF-SPI, eMMC, eMMC-SPI, PMIC, SDIO, HIF, audio, and EJTAG; selecting one function can conflict electrically with another board use. Selector pseudo-pins for SDIO, HI, GSPI, ISO-GSPI, PWM open-drain, SF enable, and EJTAG are easy to miss in board pinctrl states. Several eMMC/SPI/HIF sconfig entries have drive offsets beyond bit 31 and rely on the common core's offset rollover handling; mistakes there affect adjacent registers.

## Test Signals
Build tests should cover built-in and module configurations for `CONFIG_PINCTRL_RTD1619B`, plus a check for DT module alias behavior because the file lacks an explicit `MODULE_DEVICE_TABLE`. Probe tests should confirm `realtek,rtd1619b-pinctrl` binds and registers all groups/functions. Functional tests should exercise GPIO, NF/eMMC, SPI flash, PMIC, NF-SPI, eMMC-SPI, UART0/1/2, GSPI and ISO-GSPI loc0/loc1 plus disable states, I2C0/1/3/4/5, PWM normal/open-drain, Ethernet LED/PHY/clock, smart-card, VFD, PCIe1/2, SD/SDIO locations, HI/HI width, fan, SPDIF variants, USB CC, IR, DMIC/audio/VTC, TP/AO, serial-flash enable, ARM trace enable, and every EJTAG target/location/disable state. Pinconf validation should include GPIO-style pulls and drive strength, eMMC/SPI/HIF sconfig P/N drive and duty-cycle masks, and cross-register offset cases. Debugfs or pinctrl debug output should show the selected function for representative mux fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1619b.c -->
