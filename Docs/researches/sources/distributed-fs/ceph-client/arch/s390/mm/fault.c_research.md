## sources/distributed-fs/ceph-client/arch/s390/mm/fault.c

Purpose: handles s390 translation, protection, and secure-storage faults. It decodes TEID state, performs VMA lookup and `handle_mm_fault()` integration, reports user faults, attempts exception-table/KFENCE recovery for kernel faults, and turns unrecoverable faults into signals or oopses.

Important APIs, types, and functions: `do_protection_exception()`, `do_dat_exception()`, and, under KVM, `do_secure_storage_access()` are architecture entry points. Helpers include `is_kernel_fault()`, `get_fault_address()`, `fault_is_write()`, `dump_pagetable()`, `dump_fault_info()`, `report_user_fault()`, `handle_fault_error_nolock()`, `handle_fault_error()`, `do_sigsegv()`, `do_sigbus()`, and `do_exception()`. `show_unhandled_signals` is exposed as `kernel/userprocess_debug`.

Control flow: DAT faults call `do_exception()` with access flags; protection faults may rewind PSW for suppressing exceptions, validate TEID bit 61, special-case NX faults, then call `do_exception(VM_WRITE)`. `do_exception()` clears single-step trap state, lets kprobes handle page faults, rejects kernel/faulthandler-disabled/no-mm cases to the kernel-error path, then attempts a VMA-lock fast path for user faults before falling back to `lock_mm_and_find_vma()`. Fault results dispatch to OOM, SIGSEGV, SIGBUS, or BUG for unexpected flags. Kernel faults first try `fixup_exception()` and KFENCE before dumping table state and dying.

State and persistence: persistent state is the sysctl-backed `show_unhandled_signals`. Fault handling mutates current thread flags, pt_regs PSW address, mm fault statistics, signal state, and, for secure storage, folio secure/shared state. No durable storage is written.

Dependencies and integration points: depends on generic mm fault APIs, VMA lock fast path, kprobes, perf software events, exception tables, KFENCE, s390 TEID/ASCE layout, lowcore ASCEs, UV protected virtualization helpers, and KVM secure-storage behavior.

Risks: TEID interpretation is facility-dependent; invalid bit-61 handling is intentionally fatal for unexpected user protection exceptions. Locking paths must release mmap/VMA locks exactly once across retry and `VM_FAULT_COMPLETED`. Secure-storage conversion must hold folio references correctly and avoid kernel continuation if conversion fails. Fault address synthesis for NX combines TEID and PSW page bits and is sensitive to architecture semantics.

Test signals: page fault tests should cover user map errors, access errors, write faults, OOM/sigbus paths, VMA lock retry, kernel uaccess fixups, KFENCE faults, NX protection, no-mm/faulthandler-disabled faults, and secure guest storage conversion under KVM/UV.
