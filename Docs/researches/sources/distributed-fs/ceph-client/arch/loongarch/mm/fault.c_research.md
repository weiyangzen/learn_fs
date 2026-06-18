<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/fault.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/fault.c

### Purpose
`fault.c` is the LoongArch page-fault handler. It classifies user and kernel faults, validates VMA permissions, calls the generic memory-fault engine, reports signals, and falls back to exception fixups or kernel oops paths.

### Important APIs, Types, And Functions
Public state/API includes `show_unhandled_signals` and `do_page_fault(struct pt_regs *, unsigned long write, unsigned long address)`. Internal handlers are `spurious_fault()`, `no_context()`, `do_out_of_memory()`, `do_sigbus()`, `do_sigsegv()`, and `__do_page_fault()`. It uses `vm_fault_t`, `FAULT_FLAG_*`, `VM_FAULT_*`, `lock_vma_under_rcu()`, `lock_mm_and_find_vma()`, and `handle_mm_fault()`.

### Control Flow
`do_page_fault()` enters irqentry state, conditionally enables interrupts based on parent CSR state, then invokes `__do_page_fault()`. The core handler first lets kprobes consume the fault, rejects kernel-space/user-limit violations, and avoids taking mmap locks when fault handling is disabled or no `mm` exists. For user faults it tries the RCU VMA-lock fast path, validates write/read/exec access, calls `handle_mm_fault()`, then retries under the mmap lock if needed. Fault errors map to OOM, SIGSEGV, SIGBUS, or BUG. Kernel faults try spurious TLB acceptance, exception-table fixups, KFENCE handling, then oops.

### State, Persistence, And Dependencies
State mutations include `current->thread.csr_badvaddr`, `thread.error_code`, `thread.trap_nr`, perf software counters, VMA lock accounting, page tables through generic MM, and signal delivery. Dependencies include LoongArch CSR exception state, `asm/branch.h`, `asm/mmu_context.h`, generic MM fault code, KFENCE, kprobes, perf, context tracking, and signal APIs.

### Integration Points
The assembly TLB handlers in `tlbex.S` tail-call this for missing/protection faults. `extable.c` supplies kernel fault recovery. Generic memory management resolves demand paging, COW, file-backed page cache faults, and hugepage-related faults. For distributed filesystem behavior, this is the path by which Ceph client file mappings fault pages into user processes.

### Risks
The permission checks distinguish instruction fetches by comparing `address == exception_era(regs)`; errors can allow wrong execute/read behavior or produce incorrect SIGSEGV codes. Lockless VMA handling must release locks on all exits. Kernel-space `__UA_LIMIT` decisions and interrupt-state handling are architecture-critical.

### Test Signals
Run mmap/read/write/exec fault tests, signal-delivery tests, kprobe/KFENCE fault injection, page-fault stress under signals, Ceph/file-backed mmap tests, and LoongArch TLB miss/protection validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/fault.c -->
