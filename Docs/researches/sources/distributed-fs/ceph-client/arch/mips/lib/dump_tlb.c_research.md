# sources/distributed-fs/ceph-client/arch/mips/lib/dump_tlb.c

Purpose: dumps R4x00-style MIPS TLB registers and active entries for debugging.

Important APIs/functions: `dump_tlb_regs`, `dump_tlb_all`, and internal `dump_tlb`/`msk2str`.

Control flow: saves current TLB-related CP0 state, iterates requested TLB indices, performs `tlb_read`, skips invalid/unused/unrelated ASID/MMID entries, formats page mask, VA, ASID/MMID, optional GuestID, RI/XI bits, physical addresses, cache attributes, dirty/valid/global bits, then restores saved CP0 state.

State and persistence: temporarily changes CP0 Index/PageMask/EntryHi and optional GuestCtl1, then restores them.

Dependencies and integration: used by MIPS TLB debug paths; depends on CP0 helpers, CPU feature flags, XPA/RI/XI/HTW support, and printk.

Risks: debug code touches privileged TLB state and must restore it exactly. Formatting assumes feature-dependent widths and entry layouts.

Test signals: manual TLB dump output on supported CPUs, no state corruption after dump, and config builds with GuestID/XPA/HTW.
