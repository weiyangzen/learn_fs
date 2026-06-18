<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/usercfi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/usercfi.c

Purpose: Implements RISC-V user control-flow integrity management for Zicfiss shadow stacks and Zicfilp landing-pad enforcement.

Important APIs/types/functions: Provides shadow-stack status helpers, active/base setters/getters, `save_user_shstk()`, `restore_user_shstk()`, `SYSCALL_DEFINE3(map_shadow_stack)`, `shstk_alloc_thread_stack()`, `shstk_release()`, `arch_get/set/lock_shadow_stack_status()`, branch landing-pad get/set/lock prctls, `is_user_shstk_enabled()`, `is_user_lpad_enabled()`, and `riscv_nousercfi=` setup.

Control flow: PRCTL paths validate support, lock bits, and requested flags, allocate or release shadow-stack VMAs, update per-thread CFI state, and toggle ENVCFG bits. Signal code saves/restores shadow-stack tokens via AMO operations. Clone allocates separate stacks for CLONE_VM threads while vfork shares parent state.

State and persistence: Per-task `user_cfi_state`, `thread.envcfg`, shadow-stack VMAs, active SSP, lock bits, and global `riscv_nousercfi` command-line mask persist across task operations.

Dependencies and integration points: Integrated with process fork/exit, signal frames, ptrace CFI regset, VM shadow-stack mappings, CSR/ENVCFG handling, and RISC-V CFI CPU feature detection.

Risks: Shadow-stack token writes use privileged user access and must handle faults exactly. Double-unmap and clone/vfork edge cases can corrupt VMAs if state tracking is wrong. Lock semantics are ABI/security sensitive.

Test signals: `map_shadow_stack`, PR_SET/GET/LOCK shadow-stack and landing-pad controls, signal delivery with shadow stacks, clone/vfork/exec/exit cleanup, ptrace CFI regset, command-line disable modes, and faulted token writes.

Source read size: 532 lines, 14725 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/usercfi.c -->
