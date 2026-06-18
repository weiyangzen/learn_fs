# sources/distributed-fs/ceph-client/arch/loongarch/lib/dump_tlb.c

Purpose: prints LoongArch TLB register state and active TLB entries for debugging.

Important APIs, types, and functions: `dump_tlb_regs()` prints current TLB-related CSRs. `dump_tlb_all()` calls internal `dump_tlb(first,last)` across `current_cpu_data.tlbsize`.

Control flow: `dump_tlb()` saves current EntryHi/TLBIDX/ASID, iterates indexes, reads each TLB entry, skips invalid or nonmatching ASID entries unless global, prints page size, VA, ASID, physical halves, cache mode, dirty/valid/global, PLV, and 64-bit NR/NX flags, then restores saved CSRs.

State and persistence: temporarily changes TLB index and ASID-related CSRs while dumping, restoring them before return. No persistent state.

Dependencies and integration points: used by architecture debug paths; depends on CSR read/write helpers, `tlb_read()`, current CPU data, and printk.

Risks: dumping changes CPU CSRs transiently and must restore accurately. The local `pa` variable is conditionally initialized for 64-bit paths; build coverage matters. Output under concurrent TLB changes is diagnostic, not atomic.

Test signals: manual debug invocation, build tests for 32/64-bit configs, and verifying CSR state is preserved after dumps.
