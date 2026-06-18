<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtcrc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtcrc.c

## Purpose
`intel_pmic_chtcrc.c` provides minimal Cherry Trail Crystal Cove PMIC opregion support. Its main purpose is to register with the common Intel PMIC core so `intel_soc_pmic_exec_mipi_pmic_seq_element()` can execute display PMIC register writes on CHT Crystal Cove systems.

## Important APIs, Types, and Functions
The only variant data is `intel_chtcrc_pmic_opregion_data`, which supplies LPAT conversion and `.pmic_i2c_address = 0x6e` but no power or thermal tables. `intel_chtcrc_pmic_opregion_probe()` installs the common handlers. The built-in platform driver is named `cht_crystal_cove_pmic`.

## Control Flow and State
Probe obtains the parent `intel_soc_pmic` regmap and calls `intel_pmic_install_opregion_handler()` with the parent ACPI handle. Because table counts are zero, the common installer skips power and thermal handlers and installs only the raw register opregion, while the global common opregion pointer enables generic MIPI sequence writes for I2C address `0x6e`.

## State and Persistence
There is no chip-specific dynamic state. The installed raw register handler and global common PMIC opregion state persist for the platform-device lifetime.

## Dependencies and Integration Points
The driver depends on the Intel SoC PMIC parent, regmap, common Intel PMIC opregion core, and display/VBT users of the exported MIPI PMIC sequence helper.

## Risks and Test Signals
Risks include lack of documented power/thermal support, so AML expecting those opregions would fail, and reliance on generic MIPI register writes matching the PMIC address. Test signals are successful probe, no attempted DPTF thermal opregion access on unsupported systems, and working DSI panel initialization through PMIC sequence elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtcrc.c -->
