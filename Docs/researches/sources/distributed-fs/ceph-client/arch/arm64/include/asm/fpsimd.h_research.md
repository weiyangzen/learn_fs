## sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpsimd.h

Purpose: declares FPSIMD, SVE, SME, FA64, FPMR, and vector-length state management for arm64 tasks and CPUs.

Important APIs/types/functions: exports CPACR enable/restore helpers, FPSIMD save/load/switch/flush/update routines, `struct cpu_fp_state`, per-CPU `fpsimd_last_state`, thread SM/ZA helpers, SVE/SME state save/load/flush/VL routines, CPU enable callbacks, vector-length maps via `struct vl_info`, user enable/disable helpers, vector length setters/getters, SVE/SME state-size helpers, SME streaming mode helpers, DVMSync active tracking, and EFI FPSIMD begin/end hooks.

Control flow: context-switch and exception paths lazily preserve/restore FP/vector state, allocate SVE/SME buffers, update vector lengths, and gate user access through CPACR bits.

State and persistence: per-task FPSIMD/SVE/SME/FPMR/SVCR state, per-CPU last-state cache, global vector-length maps, and CPU control registers persist across scheduling events.

Dependencies and integration: integrates scheduler, signal ABI, ptrace, cpufeature, sysreg, EFI runtime services, KVM virtualization, and errata workarounds.

Risks: stale vector state leaks data between tasks or corrupts user registers; VL size mistakes overflow signal frames. Test signals are FPSIMD/SVE/SME selftests, signal frame tests, ptrace vector tests, context-switch stress, CPU hotplug, suspend/resume, and EFI runtime calls using FP state.
