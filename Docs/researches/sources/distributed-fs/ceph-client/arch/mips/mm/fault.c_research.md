# sources/distributed-fs/ceph-client/arch/mips/mm/fault.c

Purpose: MIPS page fault handler. It classifies user/kernel faults, handles vmalloc/module faults, enforces access permissions, invokes Linux MM fault resolution, and reports signals or kernel oopses.

Important APIs/functions: `do_page_fault()` wraps exception context tracking around `__do_page_fault()`. `__do_page_fault()` implements the fault logic and is marked `NOKPROBE_SYMBOL`. Global `show_unhandled_signals` controls user signal logging.

Control flow: notifies kprobes, handles vmalloc fault synchronization, rejects faults without user context, sets FAULT_FLAG_USER/WRITE, locks and finds VMA, checks write/read/execute permissions including RIXI support, calls `handle_mm_fault()`, handles retry/completed/error bits, sends SIGSEGV/SIGBUS for user faults, or uses `fixup_exception()`/`die()` for kernel faults. 32-bit vmalloc faults copy kernel PGD/PMD entries into the current page table.

State and persistence: updates current thread fault metadata (`cp0_badvaddr`, `error_code`, `trap_nr`) and may modify per-mm page tables in vmalloc fault.

Dependencies and integration: central trap entry for MIPS memory faults; integrates with Linux mm, perf, kprobes, context tracking, exception tables, and signal delivery.

Risks and test signals: test user read/write/exec faults, RI/XI violations, kernel uaccess fixups, OOM/SIGBUS paths, vmalloc/module faults on 32-bit, branch-delay EPC handling, and ratelimited signal logs.
