# sources/distributed-fs/ceph-client/arch/um/kernel/trap.c

## Purpose
Handles page faults and host-delivered trap signals for UML. It adapts Linux VM fault handling to UML's lack of exception tables and maps host SIGSEGV/SIGBUS/SIGILL/SIGFPE/SIGTRAP/SIGWINCH into guest faults, signals, or IRQs.

## Important APIs, Types, and Functions
`handle_page_fault()` locates/extends VMAs, calls `handle_mm_fault()`, and reports constrained error codes. `segv_handler()` and `segv()` decide whether to resolve a fault, sync kernel TLBs, recover pagefault-disabled regions, panic, or deliver SIGSEGV/SIGBUS. `fatal_sigsegv()` forces fatal SIGSEGV and core dump. `relay_signal()` sanitizes signal forwarding. `winch()` raises `WINCH_IRQ`.

## Control Flow, State, and Persistence
Fault state is stored transiently in `current->thread.arch.faultinfo`, `current->thread.segv_regs`, and optional recovery target `segv_continue`. Kernel faults in vmalloc range first try `um_tlb_sync(&init_mm)`; user faults take mmap locks carefully and may expand grow-down stacks.

## Dependencies and Integration Points
Depends on Linux mm fault core, UML faultinfo macros, TLB sync, signal core, arch fixup hooks, and host signal dispatch in `os-Linux/signal.c`/SKAS process loop.

## Risks and Test Signals
Risks include deadlocks on mmap locks after kernel bugs, wrong user/kernel fault classification, missing pagefault-disabled recovery, and unsafe signal relay layouts. Test user page faults, stack expansion, vmalloc faults, copy_from_user faults, SIGBUS from full `/dev/shm`, and fatal kernel faults.
