## sources/distributed-fs/ceph-client/arch/arm/mm/fault.c

### Purpose
Implements ARM data and prefetch abort dispatch, page fault handling, vmalloc fault synchronization, user signal delivery, kernel oops handling, and runtime FSR table patching.

### Important APIs, Types, And Functions
Important functions include `show_pte`, `do_bad_area`, `do_page_fault`, `do_translation_fault`, `do_sect_fault`, `do_DataAbort`, `do_PrefetchAbort`, `hook_fault_code`, `hook_ifault_code`, and `early_abt_enable`. Important helpers include `is_write_fault`, `vmalloc_fault`, `do_kernel_address_page_fault`, `__do_user_fault`, and `__do_kernel_fault`. `struct fsr_info` tables come from `fsr-2level.c` or `fsr-3level.c`.

### Control Flow
Abort entry computes an FSR index and calls the table handler. Page faults separate kernel-space addresses from user addresses, handle vmalloc synchronization for kernel translation faults, use kprobe and TTBR0 PAN checks, attempt RCU VMA-lock fault handling for user faults, fall back to mmap locking, call `handle_mm_fault`, and translate errors into SIGSEGV/SIGBUS/OOM or kernel fixup/oops. Prefetch aborts add `FSR_LNX_PF` to mark execute faults.

### State, Dependencies, And Integration
State is the mutable FSR/IFSR dispatch tables. Depends on generic MM fault code, signal delivery, kprobes, KFENCE, perf software events, branch predictor hardening, exception tables, and ARM page-table helpers. Integration points are low-level abort vectors and generic VM.

### Risks And Test Signals
Risks include wrong FSR decoding, sleeping in invalid contexts, missing vmalloc PMD copies, bad user/kernel address classification, signal-code regressions, and execute-fault mislabeling. Test page fault selftests, vmalloc access from kernel threads, kprobe faults, KFENCE, user SIGSEGV/SIGBUS cases, and prefetch abort behavior.
