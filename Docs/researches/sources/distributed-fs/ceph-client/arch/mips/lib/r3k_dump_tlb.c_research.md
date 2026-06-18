# sources/distributed-fs/ceph-client/arch/mips/lib/r3k_dump_tlb.c

Purpose: dumps R3000-style TLB registers and active entries for debugging.

Important APIs/functions: `dump_tlb_regs`, `dump_tlb_all`, and internal `dump_tlb`.

Control flow: saves current ASID from EntryHi, iterates indexed TLB entries with `tlbr`, skips unused KSEG0 entries and entries outside current ASID unless global, prints VA/ASID and EntryLo flags, then restores EntryHi ASID.

State and persistence: temporarily writes CP0 Index/EntryHi while dumping.

Dependencies and integration: selected by `CONFIG_CPU_R3000`; uses R3K EntryLo flag definitions and printk.

Risks: old TLB format differs from modern MIPS; using this on wrong CPU class would be invalid. Debug output lacks locking around concurrent context changes.

Test signals: R3000 build coverage and manual TLB dump sanity.
