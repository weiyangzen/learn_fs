<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_parking_protocol.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_parking_protocol.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_parking_protocol.c` implements the deprecated ACPI parking protocol CPU bring-up method for arm64 secondary CPUs. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
types: `parking_protocol_mailbox`, `cpu_mailbox_entry`, `acpi_madt_generic_interrupt`, `cpu_operations`; functions/prototypes/exports: `acpi_set_mailbox_entry`, `acpi_parking_protocol_valid`, `acpi_parking_protocol_cpu_init`, `acpi_parking_protocol_cpu_prepare`, `acpi_parking_protocol_cpu_boot`, `acpi_parking_protocol_cpu_postboot`. The file is 132 lines / 3595 bytes. Direct includes are `linux/acpi.h`, `linux/mm.h`, `linux/types.h`, `asm/cpu_ops.h`.

### Control Flow
Firmware-provided mailbox entries are recorded by `acpi_set_mailbox_entry`; CPU init validates them, prepare maps the mailbox, boot writes the kernel entry point and signals the parked CPU, and postboot clears temporary mappings.

### State, Persistence, And Dependencies
Notable global/static state symbols are `__iomem`, `cpu_mailbox_entries`, `acpi_parking_protocol_valid`, `acpi_parking_protocol_cpu_init`, `acpi_parking_protocol_cpu_prepare`, `acpi_parking_protocol_cpu_boot`, `cpu_id`, `cpu`, `entry_point`, `acpi_parking_protocol_ops`. Per-CPU mailbox metadata persists during boot. The mailbox memory is firmware-visible shared state used to release secondary CPUs. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong mailbox addresses, missing cache maintenance, or stale temporary mappings can prevent secondary CPU boot or corrupt firmware-owned memory.

### Test Signals
Build `CONFIG_ARM64_ACPI_PARKING_PROTOCOL`, boot firmware using parking protocol, test CPU online/offline, and inspect mailbox write ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi_parking_protocol.c -->
