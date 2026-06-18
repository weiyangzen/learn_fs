<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/Makefile

Purpose: Selects x86 ACPI kernel objects for boot tables, sleep/wakeup, APEI, CPPC, MADT wakeup/playdead, and processor C-state support.

Important APIs/types/functions: `obj-$(CONFIG_ACPI) += boot.o`, `obj-$(CONFIG_ACPI_SLEEP) += sleep.o wakeup_$(BITS).o`, `obj-$(CONFIG_ACPI_APEI) += apei.o`, `obj-$(CONFIG_ACPI_CPPC_LIB) += cppc.o`, `obj-$(CONFIG_ACPI_MADT_WAKEUP) += madt_wakeup.o madt_playdead.o`, and conditional `cstate.o` when `CONFIG_ACPI_PROCESSOR` is non-empty.

Control flow: Kbuild includes ACPI support objects according to config. Runtime ACPI boot, sleep, error handling, CPPC, MADT wakeup, and C-state behavior exists only when the corresponding objects are linked.

State and persistence behavior: No runtime state in the Makefile. Included objects manage ACPI table-derived state, sleep state, processor idle state, and firmware-first error handling.

Dependencies and integration points: Integrates with x86 ACPI table parsing, suspend/resume, wakeup assembly by bitness, APEI/RAS, CPPC frequency/performance controls, MADT CPU wakeup, and ACPI processor idle.

Risks and test signals: Risks include config gaps and bitness-specific wakeup object omission. Test ACPI-enabled and disabled builds, suspend/resume, APEI configs, CPPC systems, MADT wakeup CPU hotplug, and ACPI processor idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/Makefile -->
