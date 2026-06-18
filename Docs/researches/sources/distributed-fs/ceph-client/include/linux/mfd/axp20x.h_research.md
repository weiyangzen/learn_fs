## sources/distributed-fs/ceph-client/include/linux/mfd/axp20x.h

Purpose: This is the shared Allwinner/X-Powers AXP PMIC family contract. It defines variant IDs, register maps, regulator IDs, IRQ IDs, device state, a variable-width register helper, and core match/probe/remove APIs.

Important APIs, types, and constants: `enum axp20x_variants` covers AXP152, AXP192, AXP202/209, AXP221/223, AXP288, AXP313A/323, AXP717, AXP803/806/809/813, and AXP15060. Register constants cover power inputs/outputs, regulators, charger, power-off, PEK key, ADC, GPIO, battery/fuel-gauge, OCV tables, Type-C fields, and multi-bank IRQ enable/status registers. Separate regulator-ID enums define each variant's child regulator numbering. IRQ enums map event numbers across variants, intentionally preserving gaps and out-of-bit-order PEK press/release ordering where needed. `struct axp20x_dev` carries device, IRQ, regmap, regmap IRQ data, variant, MFD cells, and selected regmap/IRQ configs. `axp20x_read_variable_width()` combines adjacent 8-bit registers into a 9-16 bit value. Public APIs are `axp20x_match_device()`, `axp20x_device_probe()`, and `axp20x_device_remove()`.

Control flow: Bus-specific drivers set `dev`, create regmap, call match to select variant-specific cells/configs, then probe to register IRQs and MFD children. Child drivers use variant register constants and regulator/IRQ IDs. The inline variable-width helper performs two sequential reads and returns either a negative error or the assembled value.

State and persistence: Persistent hardware state includes RTC/charger/fuel-gauge/OCV and power-control registers, depending on PMIC power domains. Kernel runtime state lives in `axp20x_dev` and regmap/regmap-irq structures.

Dependencies and integration points: Includes `linux/regmap.h`; integrates with regulator, power-supply, GPIO, ADC/IIO, RTC, PEK input, watchdog/poweroff, Type-C/charger, and MFD frameworks.

Risks: Variant-specific register reuse is extensive; using the wrong variant ID can touch unrelated hardware. IRQ enums are not uniformly zero-based, and gaps matter for regmap IRQ tables. Variable-width reads assume high byte at `reg` and low byte at `reg + 1`; callers must pass valid widths and readable adjacent registers.

Test signals: Probe each supported variant table, compare regulator counts to `*_REG_ID_MAX`, validate IRQ bank mappings including PEK order, run regmap range/cache tests, exercise ADC variable-width reads, and verify poweroff/charger/fuel-gauge behavior on boards with real PMICs.
