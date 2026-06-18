<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vector.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vector.h

Purpose: Implements RISC-V vector extension state management interfaces for user and kernel mode, including standard V and T-Head vector variants.

Important APIs/types/functions: Key APIs are `has_vector()`, `has_xtheadvector()`, `riscv_v_enable()/disable()`, `riscv_v_vstate_save()/restore()/discard()`, `__switch_to_vector()`, kernel vector begin/end declarations, first-use handling, vector context allocation/free, and preemptible vector flags.

Control flow: Code tests extension availability, toggles VS bits, saves/restores vector CSRs and 32 vector registers, handles T-Head CSR differences, lazily restores user vector state, and saves preemptible kernel vector context on switch/trap boundaries.

State and persistence: Persistent state includes per-task `vstate`, `kernel_vstate`, vector flags, allocated vector data buffers, and global `riscv_v_vsize`.

Dependencies and integration points: Integrates with scheduler, traps, signal/ptrace regsets, cpufeature, vendor extensions, CSR helpers, and kernel SIMD users.

Risks: Vector context is large and security-sensitive; missed dirty/save transitions leak data or corrupt user/kernel vector registers, especially with preemptible vector and T-Head differences.

Test signals: Vector user ABI tests, signal/ptrace vector regsets, context-switch stress, kernel-mode vector tests, preempt/RT configs, T-Head vector hardware, and first-use fault tests.

Source read size: 444 lines, 12314 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vector.h -->
