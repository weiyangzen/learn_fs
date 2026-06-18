# sources/distributed-fs/ceph-client/arch/m68k/mm/fault.c

## Purpose
Handles m68k MMU page faults, mapping/protection errors, OOM faults, kernel fixups, and user signal delivery.

## APIs, Flow, And State
Public functions are `send_fault_sig()` and `do_page_fault()`. Fault metadata is persisted temporarily in `current->thread.signo`, `code`, and `faddr`. `do_page_fault()` rejects faults when the handler is disabled or no `mm` exists, marks user faults, emits perf page-fault events, locks the mmap, finds/expands the VMA including grow-down stack checks against `rdusp()`, validates access from the m68k error code, and calls `handle_mm_fault()`. It handles completed faults, pending signals, retry, OOM, SIGSEGV map/protection errors, and SIGBUS address errors. `send_fault_sig()` either calls `force_sig_fault()` in user mode or tries `fixup_exception()` before printing kernel access diagnostics and killing the task.

## Dependencies And Integration
Depends on Linux mm, mmap locking, perf events, uaccess exception fixups, `die_if_kernel()`, m68k trap regs, and `fault.h`. Called from m68k trap handlers and from code such as `sys_m68k.c` that simulates write faults.

## Risks And Test Signals
Lock/unlock paths are label-heavy; every error path must release mmap exactly when held. Stack growth heuristics include a 256-byte predecrement allowance. Kernel faults rely on exception-table fixups. Test signals are user SIGSEGV/SIGBUS cases, stack expansion, write-protect faults, OOM handling, retry faults, kernel copy_from_user fixups, and null-pointer kernel oops diagnostics.
