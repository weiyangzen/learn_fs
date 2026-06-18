# sources/distributed-fs/ceph-client/arch/sh/mm/tlb-urb.c

Purpose: manages wired TLB entries through the UTLB replace boundary mechanism.

Important APIs: `tlb_wire_entry` and `tlb_unwire_entry`.

Control flow: wiring installs a selected PTE as a fixed TLB entry and adjusts the replacement boundary so normal refill does not evict it. Unwiring reverses the boundary and invalidates the wired entry.

State and persistence: mutates hardware TLB entries and replacement-boundary registers; used for wired fixmap mappings.

Dependencies and integration: called by `set_pte_phys`/`clear_pte_phys` in `init.c` for `_PAGE_WIRED` mappings.

Risks: incorrect boundary accounting can evict wired mappings or reduce usable TLB capacity permanently.

Test signals: fixmap/ioremap_fixed mapping tests and TLB debugfs inspection of wired entries.
