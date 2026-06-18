<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bytcrc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bytcrc.c

## Purpose
`intel_pmic_bytcrc.c` implements ACPI operation-region support for Bay Trail Crystal Cove PMICs. It maps ACPI-defined power and thermal offsets to Crystal Cove registers and provides callbacks for rail control, raw temperature access, auxiliary thresholds, and thermal policy enable bits.

## Important APIs, Types, and Functions
The static `power_table` covers known Bay Trail rails, while `thermal_table` covers temperature and auxiliary/policy offsets. Variant callbacks are `intel_crc_pmic_get_power()`, `intel_crc_pmic_update_power()`, `intel_crc_pmic_get_raw_temp()`, `intel_crc_pmic_update_aux()`, `intel_crc_pmic_get_policy()`, and `intel_crc_pmic_update_policy()`. The registered data also sets `.pmic_i2c_address = 0x6e` for generic MIPI PMIC sequence execution.

## Control Flow and State
The built-in platform driver probes under `byt_crystal_cove_pmic`, obtains the parent `intel_soc_pmic` regmap, and installs common handlers. Power reads require both `PWR_SOURCE_SELECT` and the target bit. Power writes preserve source selection and set or clear the target bit. Raw temperature reads a 10-bit value split across register and preceding register. Auxiliary writes update low and high bits. Policy writes temporarily unlock `PMIC_A0LOCK_REG`, update bit 7, and restore the lock register.

## State and Persistence
Static mapping tables and callback data persist in the kernel image. PMIC rail, threshold, and policy settings persist in device registers. The A0 lock register is saved and restored around policy updates.

## Dependencies and Integration Points
The file depends on the Intel SoC PMIC MFD parent, regmap, common Intel PMIC core, LPAT conversion, and MIPI sequence users that address PMIC I2C `0x6e`.

## Risks and Test Signals
Risks include incomplete power table entries for unknown rails, lock-register restore failure leaving policy writes exposed, raw temperature split-register assumptions, and generic MIPI writes being allowed only for the configured I2C address. Test signals are successful probe, AML reads/writes of known rails, thermal/DPTF threshold updates, A0 lock restoration, display panel MIPI PMIC sequence success, and regmap error propagation to ACPI errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bytcrc.c -->
