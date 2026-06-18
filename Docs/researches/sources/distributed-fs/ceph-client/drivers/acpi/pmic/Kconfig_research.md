<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/Kconfig

## Purpose
`pmic/Kconfig` defines build-time options for ACPI PMIC operation region support. It groups the Intel SoC PMIC opregion core and chip-specific drivers under `PMIC_OPREGION`, while defining TPS68470 support as a separate bool because it must be available early for devices that consume its opregions.

## Important APIs, Types, and Functions
This file has no runtime functions. Important symbols are `PMIC_OPREGION`, `BYTCRC_PMIC_OPREGION`, `CHTCRC_PMIC_OPREGION`, `XPOWER_PMIC_OPREGION`, `BXT_WC_PMIC_OPREGION`, `CHT_WC_PMIC_OPREGION`, `CHT_DC_TI_PMIC_OPREGION`, and `TPS68470_PMIC_OPREGION`.

## Control Flow and State
Kconfig selection gates compilation. Enabling `PMIC_OPREGION` makes the common Intel `intel_pmic.o` buildable and exposes per-PMIC bool choices. Each child option depends on the relevant MFD/SoC PMIC provider. TPS68470 depends on `INTEL_SKL_INT3472` and stays outside the Intel menu group.

## State and Persistence
The selected symbols persist in the kernel configuration and directly determine which built-in opregion handlers are linked. These are bool options, not modules, so selected drivers are expected to be present during ACPI enumeration.

## Dependencies and Integration Points
Dependencies map each ACPI opregion driver to its MFD provider: `INTEL_SOC_PMIC`, `INTEL_SOC_PMIC_BXTWC`, `INTEL_SOC_PMIC_CHTWC`, `INTEL_SOC_PMIC_CHTDC_TI`, `MFD_AXP20X_I2C` plus built-in `IOSF_MBI`, and `INTEL_SKL_INT3472`. The file integrates with the Makefile in the same directory.

## Risks and Test Signals
Risks include missing opregion handlers if the bool is not selected, probe ordering failures if a provider is modular when an opregion must be built-in, and dependencies becoming stale as MFD driver names change. Test signals are expected object files in built-in kernel builds, ACPI devices no longer deferring on PMIC opregions, and Kconfig dependency checks for x86 tablet and camera platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/Kconfig -->
