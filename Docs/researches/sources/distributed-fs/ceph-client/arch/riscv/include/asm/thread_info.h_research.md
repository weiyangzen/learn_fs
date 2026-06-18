<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/thread_info.h

Purpose: Defines RISC-V low-level thread metadata, flags, and stack layout used by entry assembly and scheduler code.

Important APIs/types/functions: Key items are `struct thread_info`, `INIT_THREAD_INFO`, `THREAD_SIZE`, `THREAD_SHIFT`, `TIF_*` flags, syscall-work masks, and current-thread helpers.

Control flow: Entry/scheduler code reads flags to decide reschedule, signal, syscall tracing, vector restore, uaccess, and CFI work.

State and persistence: Per-task persistent state includes CPU number, preempt count, kernel/user stack pointers, syscall flags, optional SCS pointer, and user CFI state.

Dependencies and integration points: Integrates with entry.S, scheduler, signal, ptrace/seccomp, vector, SCS, and asm-offset generation.

Risks: Flag or layout drift breaks assembly entry decisions and can miss reschedules/signals or corrupt stacks.

Test signals: Boot, preemption/signal/syscall tracing, SCS/user CFI/vector configs, and asm-offset validation.

Source read size: 127 lines, 3524 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/thread_info.h -->
