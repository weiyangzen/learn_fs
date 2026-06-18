<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/hwprobe.c

Purpose: Implements the RISC-V vDSO fast path for `riscv_hwprobe` using cached all-CPU values when safe.

Important APIs/types/functions: Defines syscall wrapper `riscv_hwprobe`, helpers `riscv_vdso_get_values()`, `riscv_vdso_get_cpus()`, and `__vdso_riscv_hwprobe()`.

Control flow: The vDSO checks VVAR readiness and homogeneous CPU flags, answers all-CPU value queries from cached `vdso_arch_data`, handles WHICH_CPUS for homogeneous systems, and falls back to the real syscall for unsupported masks, not-ready data, invalid flags, or heterogeneity.

State and persistence: Reads VVAR architecture data populated by `sys_hwprobe.c`; does not mutate persistent state.

Dependencies and integration points: Coupled to `complete_hwprobe_vdso_data()`, hwprobe key layout, VVAR mapping, and vDSO syscall stubs.

Risks: Cached values must be published with correct barriers and invalidated by not-ready flags. Returning cached data for heterogeneous masks would mislead userspace.

Test signals: hwprobe syscall/vDSO parity tests, heterogeneous CPU fallback, invalid key/flag behavior, and VVAR readiness at early process startup.

Source read size: 114 lines, 2909 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/hwprobe.c -->
