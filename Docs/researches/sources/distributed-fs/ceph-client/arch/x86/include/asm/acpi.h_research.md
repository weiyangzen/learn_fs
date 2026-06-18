## `sources/distributed-fs/ceph-client/arch/x86/include/asm/acpi.h`

Purpose: x86 ACPI integration header for global ACPI knobs, GSI registration, suspend wakeup, processor capability reporting, NUMA, APEI, Xen PV remapping, and non-ACPI stubs.

Important APIs and functions: declares ACPI enable/disable flags, SCI override state, `__acpi_register_gsi`, `acpi_gsi_to_irq()`, `disable_acpi()`, `acpi_disable_pci()`, `acpi_get_wakeup_address()`, `acpi_parse_mp_wake()`, `asm_acpi_mp_play_dead()`, `acpi_processor_cstate_check()`, `arch_acpi_set_proc_cap_bits()`, root-pointer accessors, APEI memory attribute/error-report hooks, and NUMA init.

Control flow: inline helpers gate ACPI/PCI IRQ use, adjust max C-state for AMD errata/APIC C1E, advertise processor power-management capabilities based on CPU features, sanitize capabilities in Xen dom0, skip wake address setup under Xen PV, and provide stubs when `CONFIG_ACPI` is off.

State and persistence: ACPI global flags persist for boot lifetime; FADT/MADT-derived state affects IRQ routing, CPU discovery, and power management. This header mainly exposes state owned elsewhere.

Dependencies and integration points: ACPICA, x86 init hooks, NUMA, CPU feature detection, Xen, APEI/CPER, EFI memory attributes, IRQ vectors, and ACPI processor/power code.

Risks: global ACPI flags are boot-critical and affect PCI/IRQ discovery. Processor capability bits must match CPU and hypervisor behavior or firmware may choose unsafe power states. APEI mapping attributes are conservative but SME/no-encryption assumptions matter.

Test signals: ACPI boot on bare metal, ACPI-off boot, Xen PV/dom0, suspend/resume, CPU C-state exposure, ACPI NUMA, APEI error injection/reporting, and GSI registration.
