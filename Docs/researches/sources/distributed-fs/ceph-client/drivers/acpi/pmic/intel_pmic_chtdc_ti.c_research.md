<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtdc_ti.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtdc_ti.c

## Purpose
`intel_pmic_chtdc_ti.c` supports ACPI operation regions for Cherry Trail Dollar Cove TI PMICs. It maps LDO power resources and thermal ADC readings to PMIC registers and registers those mappings with the common Intel PMIC core.

## Important APIs, Types, and Functions
`chtdc_ti_power_table` maps LDO offsets to enable registers. `chtdc_ti_thermal_table` maps thermal offsets to GPADC, BPTHERM, and DIETEMP registers. Callbacks are `chtdc_ti_pmic_get_power()`, `chtdc_ti_pmic_update_power()`, and `chtdc_ti_pmic_get_raw_temp()`. Probe uses `chtdc_ti_pmic_opregion_data` and platform ID `chtdc_ti_region`.

## Control Flow and State
The platform driver obtains the parent `intel_soc_pmic` regmap and installs common opregion handlers. Power reads return bit 0 from each LDO register; writes update bit 0. Raw temperature reads a big-endian 16-bit register pair and masks it to a 10-bit value. After successful handler installation, probe clears ACPI dependencies for the PMIC companion so devices blocked on the opregion can be re-enumerated.

## State and Persistence
Static tables and installed handlers persist for the device lifetime. Power and thermal state lives in PMIC registers. Clearing ACPI dependencies changes enumeration state for devices that waited for the PMIC.

## Dependencies and Integration Points
The driver depends on the Intel SoC PMIC CHTDC TI MFD parent, regmap bulk reads, byte-order conversion, ACPI dependency handling, LPAT conversion, and the common Intel PMIC core.

## Risks and Test Signals
Risks include assuming all power resources are bit 0, 10-bit big-endian temperature layout, dependency clearing after partial platform setup, and missing auxiliary/policy callbacks for AML paths that might request them. Test signals are successful probe on `chtdc_ti_region`, dependent ACPI devices continuing enumeration, LDO toggles through AML, plausible LPAT-scaled thermal readings, and regmap bulk-read errors surfacing as ACPI failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtdc_ti.c -->
