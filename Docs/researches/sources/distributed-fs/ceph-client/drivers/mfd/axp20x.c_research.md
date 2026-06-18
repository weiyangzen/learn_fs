<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/axp20x.c

Purpose: implements the interface-independent MFD core for many X-Powers AXP PMIC variants. It defines variant-specific regmap access tables, regmap IRQ chips, child-device cell arrays, no-IRQ fallbacks, AXP806 bus address-extension handling, and a system power-off handler.

Important APIs and functions: exported APIs are `axp20x_match_device`, `axp20x_device_probe`, and `axp20x_device_remove`. `axp20x_power_off` writes the shutdown bit to the correct shutdown register. Static tables define model names, writable/volatile register ranges, regmap configs, IRQ resources, regmap IRQ chips, and MFD child arrays for AXP152, AXP192, AXP20x/22x, AXP288, AXP313A/323, AXP717, AXP803/806/809/813, and AXP15060.

Control flow: transport drivers set `dev`, `irq`, and regmap, then call `axp20x_match_device`, which reads match data, selects cells/regmap config/IRQ chip/flags, handles AXP806 cell variants, and substitutes regulator-only or variant-specific no-IRQ cell arrays when no CPU IRQ is present. `axp20x_device_probe` programs AXP806 master/slave register address extension, registers a regmap IRQ chip if an IRQ exists, adds selected MFD children, and registers a devm power-off handler for non-AXP288 variants. Removal unregisters children and the regmap IRQ chip.

State and persistence: `struct axp20x_dev` stores variant, model-specific cell table, regmap config, regmap IRQ chip data, IRQ flags, and regmap. PMIC hardware persists regulator, charger, ADC, fuel gauge, GPIO, PEK, Type-C, and shutdown state. Regmap caches are MAPLE for most variants with explicit volatile ranges.

Dependencies and integration points: depends on OF/ACPI match data from transports, regmap and regmap IRQ, MFD core, regulator and power-supply child drivers, reboot/sys-off infrastructure, and AXP20x public macros/types. Child devices receive named IRQ resources but the MFD add call does not pass the IRQ domain directly; resources map through regmap IRQ infrastructure.

Risks: the large declarative variant tables are easy to desynchronize with hardware headers or child driver expectations. No-IRQ fallback intentionally drops most children because many require interrupts, which can surprise board bring-up. `axp20x_device_remove` calls `regmap_del_irq_chip` even when no IRQ chip was registered, relying on the core data pointer state. Power-off writes ignore errors and then delays 500 ms. AXP806 address-extension mode depends on firmware properties and can affect bus accessibility for chained PMICs.

Test signals: build and probe each variant through I2C/RSB/ACPI where applicable, verify selected cell arrays including no-IRQ fallback, IRQ delivery for PEK/charger/USB/fuel-gauge events, regmap access-table enforcement, AXP806 master/slave mode writes, AXP813 IRQ mapping correction, power-off behavior for shutdown-capable variants, and child regulator/ADC/power-supply smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x.c -->
