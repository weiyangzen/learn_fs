# sources/distributed-fs/ceph-client/arch/xtensa/mm/fault.c

Purpose: Handles Xtensa page faults, vmalloc page-table synchronization, signal delivery for bad user accesses, and kernel fault fixups/oops.

Important APIs, types, and functions: `do_page_fault()`, `vmalloc_fault()`, `bad_page_fault()`, `lock_mm_and_find_vma()`, `handle_mm_fault()`, and exception-table lookup.

Control flow: Kernel faults above `TASK_SIZE` attempt `vmalloc_fault()` to copy top-level kernel page table entries from `init_mm`. Faults without context or with disabled handlers go to `bad_page_fault()`. User/kernel faults are classified as write/execute/read from `exccause`, VMA permissions are checked, `handle_mm_fault()` is invoked with retry handling, and failures generate `SIGSEGV`, `SIGBUS`, OOM handling, or kernel oops. Kernel faults first search exception tables and redirect PC to fixup if found.

State and persistence: Updates current MM page tables for vmalloc synchronization, may install PTEs via generic MM fault handling, and may mutate `regs->pc` for exception fixup.

Dependencies and integration: Tied to exception causes from traps/vectors, generic MM fault APIs, perf page-fault events, `uaccess` exception tables, and cache/TLB update callbacks.

Risks: Fault classification is architecture-cause dependent; vmalloc synchronization must validate every page-table level; retry path relies on lock release semantics; kernel bad faults terminate the task or panic through `die()`.

Test signals: User read/write/exec faults, COW, VM_FAULT_RETRY, OOM, SIGBUS mappings, vmalloc access from kernel, uaccess exception fixups, and kernel NULL/bad address oops output.
