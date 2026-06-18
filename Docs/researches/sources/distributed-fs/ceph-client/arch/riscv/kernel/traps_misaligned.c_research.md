<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/traps_misaligned.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/traps_misaligned.c

Purpose: Emulates or delegates RISC-V misaligned load/store traps, including scalar, floating-point, vector misalignment probes, unaligned-control availability, and SBI FWFT delegation setup.

Important APIs/types/functions: Provides `handle_misaligned_load()`, `handle_misaligned_store()`, vector/scalar helpers, `check_vector_unaligned_access_emulated*()`, `check_unaligned_access_emulated_all_cpus()`, `unaligned_ctl_available()`, `unaligned_access_init()`, `cpu_online_unaligned_access_init()`, and exported `misaligned_traps_can_delegate()`.

Control flow: Trap handlers decode the faulting instruction, fetch or store bytes with user/kernel access helpers, update integer or FP destination registers, and advance EPC. Boot-time probes intentionally trigger misaligned accesses on CPUs to classify whether traps are emulated. SBI FWFT setup can request firmware delegation of misaligned exceptions per CPU.

State and persistence: Maintains `unaligned_enabled`, `unaligned_ctl`, `misaligned_traps_delegated`, per-CPU scalar/vector misaligned classifications through sibling files, and CPU hotplug setup state.

Dependencies and integration points: Called by `traps.c`, feeds hwprobe and unaligned PRCTL behavior, uses FP access helpers, vector support, SBI FWFT, CPU hotplug, and exception tables.

Risks: Instruction decode coverage is broad and security-sensitive because bad emulation changes user-visible memory/registers. Kernel-mode misaligned faults must not be silently mishandled. Delegation policy differs across firmware.

Test signals: Misaligned scalar/floating/vector load/store tests, PR_UNALIGN controls, hwprobe misaligned reporting, CPU hotplug, SBI FWFT delegation, and fault-injection for inaccessible user memory.

Source read size: 648 lines, 15882 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/traps_misaligned.c -->
