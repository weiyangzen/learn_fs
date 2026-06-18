# sources/distributed-fs/ceph-client/arch/powerpc/mm/fault.c

Purpose: implements the PowerPC page-fault and bad-segment exception path, mapping architecture-specific fault bits to generic MM fault handling, signals, or kernel oops recovery.

Important APIs and control flow: `___do_page_fault()` handles debugger/kprobe short-circuits, hardware bad-fault bits, KUAP/KUEP/KFENCE kernel-fault checks, fault-disabled contexts, perf accounting, the RCU `lock_vma_under_rcu()` fast path, fallback `lock_mm_and_find_vma()`, VMA permission/pkey checks, `handle_mm_fault()` retry/completed handling, and SIGBUS/SIGSEGV/OOM conversion. `bad_page_fault()` applies exception-table fixups before dying, and Book3S64 segment interrupt handlers convert SLB/radix addressing failures.

State and dependencies: state touched includes task trap fields, VMA locks, `mmap_lock`, CMO page-in counters, perf events, and page-fault flags. It depends on DSISR/ESR definitions, radix/hash differences, pkeys, KUAP, KFENCE, kprobes, extables, and generic mm fault APIs. Risks are deadlocks while faulting under locks, misclassified KUAP faults, incorrect retry accounting, and signal mismatches for hardware poison. Test signals include user/kernel fault tests, pkey cases, KUAP copy helpers, KFENCE faults, THP/hugetlb faults, and fault injection under fatal signals.
