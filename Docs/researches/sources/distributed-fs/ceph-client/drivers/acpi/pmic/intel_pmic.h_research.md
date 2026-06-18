<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.h

## Purpose
`intel_pmic.h` defines the shared table and callback contract between the Intel PMIC opregion core and chip-specific PMIC drivers.

## Important APIs, Types, and Functions
`struct pmic_table` maps an ACPI operation-region address to a PMIC register and bit/control field. `struct intel_pmic_opregion_data` supplies variant callbacks for power, thermal raw reads, auxiliary threshold writes, policy reads/writes, MIPI sequence execution, LPAT conversion, power/thermal table pointers and counts, and a generic PMIC I2C address. The header declares `intel_pmic_install_opregion_handler()`.

## Control Flow and State
There is no runtime control flow in the header. At compile time it fixes the ABI used by variant C files to hand operation tables and functions to the common installer.

## State and Persistence
The structures describe static per-chip tables and function pointers. Once a variant passes them to the common core, they persist as opregion dispatch metadata for the PMIC device lifetime.

## Dependencies and Integration Points
The header depends on `acpi_lpat` declarations, `struct regmap`, `struct device`, and ACPI handles through included Linux headers in users. It integrates all Intel PMIC variant files with `intel_pmic.c`.

## Risks and Test Signals
Risks include callback semantic drift, table counts not matching array sizes, bit fields being interpreted differently by variants, and missing callbacks causing `-ENXIO` for AML paths. Test signals are clean builds of every variant, successful callback dispatch from power/thermal opregions, and MIPI helper behavior through either custom callback or generic I2C-address path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.h -->
