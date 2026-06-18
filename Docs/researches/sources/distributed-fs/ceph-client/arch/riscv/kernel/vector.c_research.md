<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vector.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vector.c

Purpose: Manages RISC-V vector extension sizing, context caches, first-use traps, per-task vector control PRCTL state, and default vector-access sysctl.

Important APIs/types/functions: Provides exported `riscv_v_vsize`, `riscv_v_setup_vsize()`, `riscv_v_setup_ctx_cache()`, `insn_is_vector()`, `riscv_v_thread_alloc/free()`, `riscv_v_vstate_ctrl_user_allowed()`, `riscv_v_first_use_handler()`, `riscv_v_vstate_ctrl_init()`, `riscv_v_vstate_ctrl_get_current()`, `riscv_v_vstate_ctrl_set_current()`, and sysctl init.

Control flow: Boot probes VLENB, verifies homogeneous vector length, creates user/kernel vector caches, and updates ptrace regset size. First-use traps identify vector instructions, allocate user vector state lazily, enable VS, and resume. PRCTL control enforces current/next/inherit vector access policy across exec/fork.

State and persistence: Keeps global vector size, kmem caches, default implicit-access sysctl, and per-task `vstate`, `kernel_vstate`, and `vstate_ctrl`.

Dependencies and integration points: Integrated with traps, signal frames, ptrace regsets, process fork/exec, T-Head vector compatibility, sysctl, and unaligned vector probing.

Risks: Heterogeneous VLEN is rejected but must be detected early. Lazy allocation failure signals SIGBUS. Incorrect control inheritance changes user ABI and can expose vector state unexpectedly.

Test signals: Vector first-use, PR_RISCV_V controls, sysctl default toggling, signal and ptrace vector state round trips, fork/exec inheritance, and T-Head vector systems.

Source read size: 332 lines, 8065 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vector.c -->
