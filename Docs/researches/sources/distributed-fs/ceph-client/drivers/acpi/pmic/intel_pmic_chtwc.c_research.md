<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtwc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtwc.c

## Purpose
`intel_pmic_chtwc.c` implements ACPI operation-region support for Cherry Trail Whiskey Cove PMICs. It provides regulator/rail power mappings and a custom MIPI PMIC sequence handler for the 16-bit address format used by this PMIC family.

## Important APIs, Types, and Functions
The file defines many Whiskey Cove register constants, a `power_table` for rails such as V18A, V18X, VDDQ, VSDIO, and VPROG rails, callbacks `intel_cht_wc_pmic_get_power()`, `intel_cht_wc_pmic_update_power()`, and `intel_cht_wc_exec_mipi_pmic_seq_element()`, plus platform probe using `intel_cht_wc_pmic_opregion_data`.

## Control Flow and State
The built-in driver matches `cht_wcove_region`, gets the parent PMIC regmap, and installs common handlers. Power reads test a configured bitmask; writes call `regmap_update_bits()` with either 1 or 0. MIPI sequence execution validates 8-bit I2C client and register addresses, composes a regmap address as `(client << 8) | reg`, and updates masked bits. Thermal table/count are intentionally empty because DPTF thermal support lacks documentation.

## State and Persistence
State is static tables and installed handlers. PMIC register writes persist in hardware. No dynamic per-variant state is maintained.

## Dependencies and Integration Points
The driver depends on the Intel SoC PMIC CHT Whiskey Cove MFD, regmap, common Intel PMIC core, ACPI LPAT declarations, and display drivers that execute MIPI PMIC sequence elements.

## Risks and Test Signals
Risks include using `on ? 1 : 0` with multi-bit masks, incomplete/undocumented rails, no thermal opregion support, and MIPI address-range rejection for firmware sequences that encode wider addresses. Test signals are successful `cht_wcove_region` probe, AML rail toggles for mapped offsets, display panel MIPI sequence writes, and lack of DPTF thermal failures on supported systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtwc.c -->
