<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/process.c

Purpose: Supplies RISC-V process and thread lifecycle support: idle, register display, ELF/compat setup, user-thread start state, fork/clone register construction, vector and shadow-stack cleanup, tagged-address controls, and sysctl/init hooks.

Important APIs/types/functions: Key functions include `arch_cpu_idle()`, `set_unalign_ctl()`, `get_unalign_ctl()`, `__show_regs()`, `show_regs()`, `arch_align_stack()`, `compat_elf_check_arch()`, `start_thread()`, `flush_thread()`, `arch_release_task_struct()`, `arch_dup_task_struct()`, `ret_from_fork_kernel()`, `ret_from_fork_user()`, `copy_thread()`, `arch_task_cache_init()`, `set_tagged_addr_ctrl()`, `get_tagged_addr_ctrl()`, and tagged-address sysctl init.

Control flow: New execs clear and initialize pt_regs, status bits, FP/vector/CFI state, and ABI mode before jumping to the user PC/SP. Fork copies architecture thread state, clears child return registers, picks kernel or user fork trampolines, handles `CLONE_SETTLS`, optionally allocates a separate shadow stack, and initializes vector control inheritance. Tagged-address control validates PR flags, PMLEN support, and global disable state before changing per-thread environment configuration.

State and persistence: Persistent state is in `thread_struct`, `thread_info`, pt_regs, vector datap buffers, shadow-stack metadata, `envcfg`, and static tagged-address capability flags. Boot/init code records compat support and tagged-address PMLEN availability.

Dependencies and integration points: Ties scheduler fork/exit, ELF loader, ptrace-visible registers, vector context caches, user CFI shadow stacks, unaligned control, and PR_SET_TAGGED_ADDR_CTRL/PR_GET_TAGGED_ADDR_CTRL ABI together.

Risks: Fork/exec state must not leak FP/vector/CFI state across tasks. Tagged address controls are security-sensitive because they alter accepted user pointer ranges. Shadow-stack allocation failure during clone must unwind correctly.

Test signals: 32-bit compat exec on RV64, clone/fork/vfork with TLS and shadow stacks, vector first-use after fork/exec, tagged-address PRCTL combinations and sysctl disable, register dumps after traps, and unaligned-control PRCTL tests.

Source read size: 446 lines, 11883 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/process.c -->
