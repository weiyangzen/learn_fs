<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/Makefile

## Purpose
`pmic/Makefile` maps ACPI PMIC opregion Kconfig symbols to the object files that implement common Intel and chip-specific handlers.

## Important APIs, Types, and Functions
There are no runtime APIs. Build targets are `intel_pmic.o`, `intel_pmic_bytcrc.o`, `intel_pmic_chtcrc.o`, `intel_pmic_xpower.o`, `intel_pmic_bxtwc.o`, `intel_pmic_chtwc.o`, `intel_pmic_chtdc_ti.o`, and `tps68470_pmic.o`.

## Control Flow and State
Kbuild adds objects with `obj-$(CONFIG_...)`. The common Intel core is tied to `CONFIG_PMIC_OPREGION`; variant drivers are tied to their individual symbols; TPS68470 is controlled separately.

## State and Persistence
The file affects build artifacts only. Since the associated Kconfig symbols are bools, selected objects are linked into the kernel image rather than built as loadable modules.

## Dependencies and Integration Points
The Makefile integrates directly with `pmic/Kconfig` and the ACPI driver build. Variant objects depend on `intel_pmic.o` when they call `intel_pmic_install_opregion_handler()` or `intel_soc_pmic_exec_mipi_pmic_seq_element()`.

## Risks and Test Signals
Risks are straightforward build coupling: adding a Kconfig symbol without an object mapping leaves support absent, and compiling a variant without the common object would break linkage. Test signals are successful `drivers/acpi/pmic/` builds for each enabled symbol and expected built-in opregion probe logs on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/Makefile -->
