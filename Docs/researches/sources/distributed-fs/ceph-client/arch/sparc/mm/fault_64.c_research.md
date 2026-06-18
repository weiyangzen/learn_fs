# sources/distributed-fs/ceph-client/arch/sparc/mm/fault_64.c

Purpose: SPARC64 page-fault handler for ITLB/DTLB misses, write/access faults, kernel exception fixups, non-faulting loads, stack growth, TSB growth, and huge TSB setup.

Important APIs/functions: `do_sparc64_fault(struct pt_regs *regs)` is the main entry. Helpers include `get_user_insn`, `do_fault_siginfo`, `get_fault_insn`, `do_kernel_fault`, `bad_kernel_pc`, and `bogus_32bit_fault_tpc`. Global `show_unhandled_signals` controls signal logging.

Control flow: the handler enters exception context, reads thread fault code/address, lets kprobes consume faults, validates 32-bit task address widths and privileged PCs, rejects atomic/no-mm contexts, emits perf page-fault events, locks `mmap_lock` with trylock optimization for kernel faults, resolves VMA and stack growth, optionally decodes the faulting instruction to infer writes on pure DTLB misses, validates ITLB execute and write/read permissions, calls `handle_mm_fault`, handles retry/completed/error/OOM/SIGBUS cases, grows base and huge TSBs according to RSS counters, and exits exception context. Kernel faults search exception tables, handle non-faulting loads by clearing destination registers or special `ldf/stq`, or die.

State and persistence: mutates page tables through `handle_mm_fault`, grows per-mm TSBs, updates thread fault code for Spitfire executable write block-commit, advances `tpc/tnpc` for exception fixups/non-faulting loads, sends signals, and may log diagnostics.

Dependencies/integration: uses kprobes, context tracking, exception tables, SPARC ASIs, LSU/fault-code bits, TSB management (`tsb_grow`, `hugetlb_setup`), huge/THP counters, instruction decoding helpers, and core mm.

Risks: write inference from instruction bits is best-effort and must exclude prefetches. Non-faulting load handling relies on ASI decoding. Kernel PC validation must keep module/init ranges in sync. TSB growth after faults depends on RSS counters adjusted for THP. Faulting while `mmap_read_trylock` fails has a special kernel path to avoid sleeping without fixup.

Test signals: SPARC64 user read/write/exec faults, 32-bit compat faults above 4GB, kernel exception-table copy paths, non-faulting load faults, stack auto-growth vs non-faulting load no-growth, THP/hugetlb first faults that trigger huge TSB setup, kprobe page-fault tests, OOM/SIGBUS paths, and TSB growth counters.
