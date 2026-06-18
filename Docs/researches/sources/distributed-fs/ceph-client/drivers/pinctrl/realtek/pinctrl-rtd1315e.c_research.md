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
