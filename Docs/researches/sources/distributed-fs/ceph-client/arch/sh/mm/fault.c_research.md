# sources/distributed-fs/ceph-client/arch/sh/mm/fault.c

Purpose: implements SH MMU page fault handling for user, kernel, vmalloc/module, kprobe, and trapped-I/O faults.

Important functions: `do_page_fault`, `vmalloc_fault`, `vmalloc_sync_one`, `no_context`, `bad_area*`, `do_sigbus`, `mm_fault_error`, `access_error`, `fault_in_kernel_space`, `show_pte`, and `show_fault_oops`.

Control flow: kernel-space faults first try vmalloc page-table synchronization and kprobe handling, then bad-area recovery. User faults enable interrupts when appropriate, count perf page faults, reject disabled/no-mm contexts, find and lock the VMA, verify access rights, call `handle_mm_fault`, and process retry/error outcomes. Kernel no-context faults try exception-table and trapped-I/O fixups before oopsing.

State and persistence: mutates current page tables during vmalloc sync and normal fault handling, thread fault code, signal state, and perf counters.

Dependencies and integration: generic MM fault machinery, kprobes, perf, exception tables, trapped I/O, TLB/MMU context, signal delivery, and page-table helpers.

Risks: lock/retry handling around `mmap_read_lock` and `VM_FAULT_COMPLETED/RETRY` must be exact. Kernel faults in interrupt/critical regions cannot sleep. Highmem page-table printing avoids invalid mappings.

Test signals: page fault stress, mmap permission faults, vmalloc/module access from different tasks, kprobe faults, OOM/SIGBUS paths, and uaccess exception recovery.
