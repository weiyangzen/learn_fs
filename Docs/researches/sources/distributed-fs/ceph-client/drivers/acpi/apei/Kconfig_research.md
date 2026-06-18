## sources/distributed-fs/ceph-client/drivers/acpi/apei/Kconfig

Purpose: this `Kconfig` defines Linux kernel configuration symbols for ACPI Platform Error Interface support and its subfeatures: GHES, PCIe AER integration, ARM64 SEA, memory failure recovery, EINJ, CXL EINJ, NVIDIA GHES vendor records, and ERST debug support.

Important symbols: `HAVE_ACPI_APEI` and `HAVE_ACPI_APEI_NMI` are architecture capability booleans. `ACPI_APEI` enables the base framework and selects `MISC_FILESYSTEMS`, `PSTORE`, and `UEFI_CPER`. `ACPI_APEI_GHES` enables Generic Hardware Error Source and selects ACPI HED, IRQ work, generic allocator, and ARM SDE on ARM64. `ACPI_APEI_PCIEAER`, `ACPI_APEI_SEA`, `ACPI_APEI_MEMORY_FAILURE`, `ACPI_APEI_EINJ`, `ACPI_APEI_EINJ_CXL`, `ACPI_APEI_GHES_NVIDIA`, and `ACPI_APEI_ERST_DEBUG` gate focused integrations.

Control flow: Kconfig dependencies express build eligibility. Selecting `ACPI_APEI` unlocks subordinate options; `ACPI_APEI_EINJ_CXL` additionally requires CXL bus compatibility with the EINJ tristate.

State and dependencies: this file does not define runtime state. It controls which object files and feature code are compiled and which framework dependencies are pulled into the kernel configuration.

Integration points: the `apei/Makefile` consumes these symbols to build `apei.o`, `ghes.o`, `einj.o`, vendor handlers, and debug modules. Architecture Kconfig must provide `HAVE_ACPI_APEI`.

Risks: incorrect dependencies can expose unsupported firmware-first paths on architectures without required interrupt/NMI handling. Tristate compatibility for CXL EINJ must prevent linking built-in code against unavailable module code.

Test signals: configuration matrix builds for disabled base, base-only, GHES, EINJ as built-in/module, CXL EINJ with CXL bus tristate variations, NVIDIA handler, ERST debug, ARM64 SEA defaulting, and missing `HAVE_ACPI_APEI` should be checked.
