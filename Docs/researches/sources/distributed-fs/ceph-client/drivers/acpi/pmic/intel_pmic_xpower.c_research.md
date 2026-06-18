<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_xpower.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_xpower.c

## Purpose
`intel_pmic_xpower.c` implements ACPI opregion support for XPower AXP288 PMICs. It maps regulator and thermal ACPI offsets to AXP288 regmap operations, coordinates IOSF P-unit I2C access, provides GPADC temperature reads, handles display MIPI PMIC sequence writes, and installs a dummy GPIO opregion handler for firmware compatibility.

## Important APIs, Types, and Functions
Static `power_table` maps ALD/DLD/ELD/FLD/BUC/GPI1 regulators. `thermal_table` maps TMP0-TMP5 to GPADC. Key callbacks are `intel_xpower_pmic_get_power()`, `intel_xpower_pmic_update_power()`, `intel_xpower_pmic_get_raw_temp()`, `intel_xpower_exec_mipi_pmic_seq_element()`, `intel_xpower_lpat_raw_to_temp()`, and `intel_xpower_pmic_gpio_handler()`. Probe installs both GPIO and PMIC opregion handlers.

## Control Flow and State
Probe gets the parent `axp20x_dev`, installs an ACPI GPIO address-space handler that returns `AE_OK`, then installs common PMIC handlers with AXP288 regmap data. Regulator writes block P-unit I2C access before touching PMIC registers; GPI1 LDO uses a special three-bit on/off encoding. GPADC reads temporarily switch the TS current source to on-demand when needed, waits, blocks P-unit access, bulk reads ADC bytes, restores TS current-source mode, and unblocks access. MIPI sequence writes require I2C address `0x34` and update masked bits under IOSF blocking.

## State and Persistence
Static mappings persist in the kernel. Hardware regulator, TS-current, and PMIC register states persist in the PMIC. The GPIO opregion handler has no state and is installed only to satisfy AML access.

## Dependencies and Integration Points
Dependencies include the AXP20x MFD parent, regmap, IOSF MBI locking, common Intel PMIC core, LPAT conversion, ACPI GPIO address-space handling, and display MIPI sequence users.

## Risks and Test Signals
Risks include failing to restore TS current mode on some error paths, IOSF lock/unlock ordering, special GPI1 LDO encoding, LPAT clamping hiding firmware table range defects, and dummy GPIO handling masking AML expectations. Test signals are successful probe on `axp288_pmic_acpi`, regulator AML toggles without P-unit conflicts, plausible temperature readings with TS current restored, MIPI writes to address `0x34`, and no ACPI GPIO opregion errors during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_xpower.c -->
