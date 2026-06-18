<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.c

## Purpose
`intel_pmic.c` is the common Intel SoC PMIC ACPI operation-region core. It installs address-space handlers for PMIC power, thermal, and raw register opregions, translates ACPI opregion addresses to PMIC regmap accesses through chip-specific tables, applies optional LPAT temperature conversion, and exports a MIPI PMIC sequence helper for display initialization.

## Important APIs, Types, and Functions
Private state is `struct intel_pmic_opregion`, holding a lock, LPAT table, regmap, variant data, and raw register-handler context. Public exports are `intel_pmic_install_opregion_handler()` and `intel_soc_pmic_exec_mipi_pmic_seq_element()`. Key handlers are `intel_pmic_power_handler()`, `intel_pmic_thermal_handler()`, and `intel_pmic_regs_handler()`. Helper paths include `pmic_get_reg_bit()`, `pmic_read_temp()`, `pmic_thermal_aux()`, and `pmic_thermal_pen()`.

## Control Flow and State
Variant probe calls `intel_pmic_install_opregion_handler()` with a parent ACPI handle, regmap, and `intel_pmic_opregion_data`. The core allocates state, initializes LPAT conversion, conditionally installs power and thermal handlers when tables are nonempty, always installs the raw register handler, and records the global opregion pointer. ACPI reads/writes validate 32-bit accesses, resolve opregion address to table entry, lock the opregion, and call variant callbacks. The raw register opregion stages high/low address and value bytes across offsets 1-3, executes read/write at offset 4, and returns read value at offset 3.

## State and Persistence
Persistent state includes installed ACPI handlers, the LPAT conversion table, raw register context bytes, and the global singleton `intel_pmic_opregion` used by MIPI sequence execution. Hardware state persists in PMIC registers changed through regmap.

## Dependencies and Integration Points
The core depends on ACPI address-space handlers, `acpi_lpat`, regmap, Intel SoC PMIC MFD drivers, and chip-specific `intel_pmic_opregion_data` tables. The MIPI helper integrates with display drivers that need PMIC register writes from VBT MIPI sequences.

## Risks and Test Signals
Risks include singleton global state when multiple PMIC opregions exist, no explicit handler removal path in the common installer, raw register context shared across AML accesses, table/address mismatches returning ACPI errors, and variant callbacks determining actual electrical behavior. Test signals are successful handler installation, AML power/thermal reads and writes, LPAT conversion correctness, MIPI sequence writes on DSI panels, and failure unwinding when a later handler install fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.c -->
