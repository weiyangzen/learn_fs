# sources/distributed-fs/ceph-client/arch/sparc/mm/fault_32.c

Purpose: SPARC32 page-fault and register-window fault handling.

Important APIs/functions: `do_sparc_fault(regs, text_fault, write, address)` is the main fault entry. Helpers include `unhandled_fault`, `show_signal_msg`, `compute_si_addr`, `do_fault_siginfo`, `force_user_fault`, `window_overflow_fault`, `window_underflow_fault`, and `window_ret_fault`. Global `show_unhandled_signals` gates segfault logging.

Control flow: the main handler normalizes text faults to `regs->pc`, routes kernel vmalloc addresses through `vmalloc_fault`, rejects faults in atomic/no-mm contexts, locks/fetches VMA with `lock_mm_and_find_vma`, validates access permissions, calls `handle_mm_fault`, handles retry/completed/error cases, and signals user mode or searches exception tables for kernel mode. `vmalloc_fault` copies missing top-level kernel mappings from `init_mm`. Window fault helpers fault in stack save/restore areas and enforce 8-byte stack alignment.

State and persistence: mutates process page tables through `handle_mm_fault`/vmalloc synchronization, updates `regs->pc/npc` for exception fixups, and sends signals. No private persistent data besides `show_unhandled_signals`.

Dependencies/integration: uses core mm fault APIs, exception tables, perf page-fault events, SPARC register/window address computation, `mm_32.h`, SRMMU page table structures, and signal delivery.

Risks: in the `no_context` kernel path the code assigns `entry->fixup` without a visible null check, so it relies on reaching that path only when an exception table entry exists or on architecture expectations not shown here. Accurate effective-address computation is needed for user `si_addr`. Stack window faults cross page boundaries and can recurse into page fault handling.

Test signals: user SIGSEGV/SIGBUS tests for read/write/exec faults, vmalloc fault synchronization, exception-table protected copy routines, register-window overflow/underflow/ret faults across page boundaries, OOM fault handling, and perf page-fault counters.
