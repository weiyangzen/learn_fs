# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-invert.h

Purpose: provides helpers that invert the PFN bits of non-present, non-empty PTEs to mitigate speculative use of physical addresses in PROT_NONE or swap-like entries.

Important APIs, types, and functions: inline helpers are `__pte_needs_invert(u64 val)`, `protnone_mask(u64 val)`, and `flip_protnone_guard(u64 oldval, u64 val, u64 mask)`.

Control flow: `__pte_needs_invert()` returns true for nonzero entries without `_PAGE_PRESENT`; zero clear entries are excluded. `protnone_mask()` returns all ones when inversion is needed. `flip_protnone_guard()` detects transitions into or out of the inversion-needed state and flips PFN bits under the supplied mask while preserving non-PFN flags.

State and persistence: no state is owned. The helpers transform page-table values before storage or interpretation.

Dependencies and integration points: included by PAE and x86-64 page-table headers. It depends on `_PAGE_PRESENT` and caller-supplied PFN masks, and integrates with `pte_pfn()`/entry construction logic that undoes the inversion.

Risks: zero entries must not be inverted. Transition detection must be applied consistently, or PTE PFNs will be double-inverted or left exposed. This is part of the L1TF/speculation mitigation surface.

Test signals: PROT_NONE mappings, swap/migration entries, L1TF mitigation tests, PTE transition tests through mprotect/unmap/fault, and PFN extraction round trips for inverted and normal entries.
