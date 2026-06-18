# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/Makefile

## Purpose
This Makefile controls which x86 local APIC, IO-APIC, IPI, MSI, NMI, and x2APIC implementation objects are built. It also disables KCOV instrumentation for this directory because APIC timer interrupts introduce nondeterministic coverage unrelated to syscall inputs.

## Important APIs, Types, and Functions
- Build policy: `KCOV_INSTRUMENT := n`.
- Local APIC objects under `CONFIG_X86_LOCAL_APIC`: `apic.o`, `apic_common.o`, `apic_noop.o`, `ipi.o`, `vector.o`, `init.o`, and `probe_$(BITS).o`.
- Always-built object: `hw_nmi.o`.
- IOAPIC/MSI/SMP objects: `io_apic.o`, `msi.o`, and `ipi.o` under their corresponding configs.
- 64-bit x2APIC/probe ordering: `apic_numachip.o`, `x2apic_uv_x.o`, `x2apic_savic.o`, `x2apic_phys.o`, `x2apic_cluster.o`, and `apic_flat_64.o`.

## Control Flow
Kbuild evaluates configuration symbols and appends matching objects to `obj-y` or `obj-*`. The object order is significant: the 64-bit APIC probe depends on listing order, and the 32-bit `probe_$(BITS).o` object is explicitly listed last.

## State and Persistence Behavior
The file has no runtime state, but it persists architecture build composition. Changing object order or config conditions changes which APIC drivers are linked and the order in which probe data is available.

## Dependencies and Integration Points
It integrates x86 APIC source files with Kbuild, KCOV, local APIC configuration, IOAPIC, PCI MSI, SMP IPI support, Numachip, UV, AMD Secure AVIC, and x2APIC physical/cluster modes. The compiled objects are consumed by early APIC probing and interrupt setup used by ACPI/MADT boot code.

## Risks
- Reordering 64-bit APIC objects can change APIC probe selection.
- Instrumenting APIC interrupt code with KCOV would make coverage nondeterministic.
- `ipi.o` appears under both local APIC and SMP conditions; configuration changes must avoid duplicate or missing linkage.
- Moving 32-bit probe earlier can break the explicit "listed last" requirement.

## Test Signals
- Build matrix with `CONFIG_X86_LOCAL_APIC`, `CONFIG_X86_IO_APIC`, `CONFIG_PCI_MSI`, `CONFIG_SMP`, and 64-bit x2APIC platform options.
- Inspect link order in verbose Kbuild output when changing APIC probe objects.
- Run KCOV workloads and confirm APIC timer interrupts do not create random coverage.
