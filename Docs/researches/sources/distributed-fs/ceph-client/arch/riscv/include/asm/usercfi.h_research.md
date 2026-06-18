<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/usercfi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/usercfi.h

Purpose: Declares user-mode control-flow-integrity state, especially shadow-stack support, for RISC-V.

Important APIs/types/functions: Defines `struct user_cfi_state`, shadow-stack flags/helpers, syscall/prctl hooks, signal helpers, and no-op fallbacks when disabled.

Control flow: Enabled builds save/restore user shadow-stack pointers across context switch, signal delivery, exec, and prctl/syscall operations.

State and persistence: Per-thread persistent state includes user shadow-stack pointer and CFI enablement flags in `thread_info`/task state.

Dependencies and integration points: Integrates with Zicfiss/FWFT support, signal frames, switch_to, ptrace/prctl, and memory permissions for shadow stacks.

Risks: Bad state transitions can weaken CFI or make user tasks unrecoverably fault on return.

Test signals: User CFI/shadow-stack selftests, signal/altstack, exec/fork/clone, ptrace, and SBI FWFT feature tests.

Source read size: 97 lines, 3102 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/usercfi.h -->
