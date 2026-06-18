# sources/distributed-fs/ceph-client/arch/arc/mm/fault.c

Purpose: handles ARC page faults for TLB misses and protection violations that cannot be satisfied by the assembly fast path.

Important APIs/functions: `do_page_fault()` is the main exception entry. `handle_kernel_vaddr_fault()` synchronizes a task page table with the kernel reference page table for vmalloc/pkmap/fixmap addresses.

Control flow: kernel vmalloc faults copy top-level page-table entries without taking normal locks. Other faults reject interrupt/no-mm contexts, decode write/exec from ECR, set generic fault flags, locate and validate the VMA, call `handle_mm_fault()`, handle signal/retry/completed cases, and deliver SIGSEGV/SIGBUS or call `die()` if unrecoverable in kernel. Kernel no-context faults try `fixup_exception()` before oops.

State and persistence: updates `current->thread.fault_address` on user signal delivery. Page tables and VM fault state are modified by generic mm. It reads ECR cause/vector from `pt_regs`.

Dependencies and integration: integrates with `tlbex.S` slow path, generic mm fault handling, perf page fault events, exception-table fixups, and diagnostics in traps/troubleshoot.

Risks: lock handling around `lock_mm_and_find_vma()` and `VM_FAULT_COMPLETED/RETRY` must remain correct. Permission decoding from ARC ECR must match hardware. Kernel vmalloc fault synchronization cannot sleep or take broad locks.

Test signals: user read/write/exec faults, COW and stack growth, vmalloc/module access faults, uaccess fixups, OOM/SIGBUS paths, and perf page fault counters.
