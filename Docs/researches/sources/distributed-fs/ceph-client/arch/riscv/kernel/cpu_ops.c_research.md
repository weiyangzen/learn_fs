# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops.c

Purpose: Selects the CPU bringup operations implementation used for secondary harts.

Important APIs/types/functions: Provides `cpu_ops[]`/selection logic around available `struct cpu_operations` implementations such as SBI HSM and spinwait.

Control flow: Early SMP setup chooses a CPU operations backend based on firmware/device-tree compatibility and build configuration. Later CPU start/stop calls go through the selected backend.

State and persistence: Stores selected CPU operation pointers used for the lifetime of the booted kernel.

Dependencies and integration points: Integrates with `cpu_ops_sbi.c`, `cpu_ops_spinwait.c`, SMP boot, hotplug, device tree CPU enable methods, and SBI availability.

Risks and test signals: Wrong backend selection can prevent secondary CPUs from starting or stopping. Test boot on SBI HSM systems, legacy spinwait systems, bad enable-method DT nodes, and CPU hotplug.
