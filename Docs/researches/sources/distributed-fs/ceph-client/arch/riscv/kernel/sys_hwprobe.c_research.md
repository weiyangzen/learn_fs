<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_hwprobe.c

Purpose: Implements the `riscv_hwprobe` syscall and vDSO data cache population so userspace can discover CPU IDs, ISA extensions, cache block sizes, unaligned-access behavior, timebase, virtual-address limits, and vendor extensions across CPU masks.

Important APIs/types/functions: Key helpers include `hwprobe_arch_id()`, `hwprobe_isa_ext0()`, `hwprobe_isa_ext1()`, `hwprobe_misaligned()`, `hwprobe_vec_misaligned()`, `hwprobe_one_pair()`, `hwprobe_get_values()`, `hwprobe_get_cpus()`, async probe registration/completion, `complete_hwprobe_vdso_data()`, `do_riscv_hwprobe()`, and `SYSCALL_DEFINE5(riscv_hwprobe)`.

Control flow: Syscall entry waits once for asynchronous boot probes, then either fills key/value pairs for a CPU mask or filters a CPU mask to CPUs matching requested pairs. Key dispatch computes homogeneous values across online CPUs, clears unsupported or non-common extension bits, and marks unknown keys with `key = -1`. The vDSO cache is filled for all online CPUs and published with a write barrier.

State and persistence: Uses boot-probe completion/atomic state, per-CPU misaligned speed values, global CPU feature bitmaps, `riscv_timebase`, cache block sizes, and vDSO `vdso_arch_data` readiness/homogeneity flags.

Dependencies and integration points: Integrates cpufeature discovery, unaligned-speed probing, vector support, vendor-extension hwprobe files, `vdso/hwprobe.c`, and the userspace syscall ABI documented for RISC-V.

Risks: Reporting an extension without kernel enablement can break userspace. CPU-mask semantics must handle heterogeneous systems, hotplug, invalid keys, and empty masks. vDSO publication ordering is subtle.

Test signals: `riscv_hwprobe` syscall tests for all keys, WHICH_CPUS filtering, heterogeneous CPU masks, unknown keys, vDSO fast path versus syscall fallback, async probe completion, and vendor extension bits.

Source read size: 612 lines, 16448 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_hwprobe.c -->
