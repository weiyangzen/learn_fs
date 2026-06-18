<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bxtwc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bxtwc.c

## Purpose
`intel_pmic_bxtwc.c` implements ACPI PMIC operation-region support for Broxton Whiskey Cove PMICs. It supplies power rail mappings, thermal sensor mappings, ADC conversion logic, auxiliary threshold programming, and policy bit handlers to the common Intel PMIC core.

## Important APIs, Types, and Functions
Static `power_table` maps ACPI power region offsets to voltage rail control registers and enable bits or modes. `thermal_table` maps thermal opregion offsets to ADC/alert registers and policy bits. Variant callbacks are `intel_bxtwc_pmic_get_power()`, `intel_bxtwc_pmic_update_power()`, `intel_bxtwc_pmic_get_raw_temp()`, `intel_bxtwc_pmic_update_aux()`, `intel_bxtwc_pmic_get_policy()`, and `intel_bxtwc_pmic_update_policy()`. Probe registers `intel_bxtwc_pmic_opregion_data`.

## Control Flow and State
The built-in platform driver matches `bxt_wcove_region`. Probe obtains the parent `intel_soc_pmic` regmap and calls the common installer with the parent ACPI handle. Power reads test configured bits; writes update the bit/mask to all ones or zero. Raw temperature reads low and high ADC bytes, extracts current source, scales by an `rlsb_array`, and returns an ADC-derived raw value. Auxiliary threshold writes compute current select and threshold fields and program high/low alert registers. Policy callbacks read or write individual bits.

## State and Persistence
Persistent state is the static mapping tables and installed handlers. PMIC register changes persist in hardware until changed by firmware, AML, or drivers. No per-variant dynamic state is kept beyond common opregion data.

## Dependencies and Integration Points
The driver depends on the Intel SoC PMIC MFD parent, regmap, common Intel PMIC opregion core, ACPI LPAT conversion, and the platform-device ID created for Broxton Whiskey Cove regions.

## Risks and Test Signals
Risks include ADC current-source index assumptions, threshold math edge cases for low raw values, enable semantics differing between VR modes and switch bits, and register map differences across PMIC revisions. Test signals are handler probe on `bxt_wcove_region`, AML power rail toggles, thermal readings matching LPAT-scaled sensors, DPTF policy bit writes, and no regmap I/O errors during suspend/resume thermal polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bxtwc.c -->
