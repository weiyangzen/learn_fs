<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_ops.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_ops.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_ops.c` selects per-CPU boot operations for arm64 CPUs from device tree or ACPI enable-method data. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
types: `device_node`, `cpu_operations`; functions/prototypes/exports: `cpu_get_ops`, `cpu_read_enable_method`, `init_cpu_ops`. The file is 118 lines / 2641 bytes. Direct includes are `linux/acpi.h`, `linux/cache.h`, `linux/errno.h`, `linux/of.h`, `linux/string.h`, `asm/acpi.h`, `asm/cpu_ops.h`, `asm/smp_plat.h`.

### Control Flow
`init_cpu_ops` reads the CPU enable method, looks up a matching `cpu_operations` table, validates it, and stores it for later secondary CPU bring-up; `get_cpu_ops` returns the selected table.

### State, Persistence, And Dependencies
Notable global/static state symbols are `__init`. The `cpu_ops` array is initialized once and then kept read-only after init, defining how each CPU is started. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Missing or mismatched enable-method strings can prevent secondary CPUs from booting, especially across DT, PSCI, spin-table, or ACPI parking protocol systems.

### Test Signals
Boot DT and ACPI systems with PSCI/spin-table/parking methods, test CPU hotplug, and validate error logs for unsupported enable methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_ops.c -->
