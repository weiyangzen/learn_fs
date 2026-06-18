# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-3level.S

## Purpose
This file provides the ARMv7 LPAE, three-level page-table implementation pieces: 64-bit TTBR updates, 64-bit PTE installation, MAIR constants, TTBCR/TTBR1 setup macro, and control-register values.

## Important APIs, Types, and Functions
It defines `cpu_v7_switch_mm()` for LPAE TTBR0 writes via `mcrr`, `cpu_v7_set_pte_ext()` for 64-bit L3 PTE updates, endian-dependent register aliases, MAIR-equivalent `PRRR`/`NMRR` constants, `v7_ttb_setup`, and `v7_crval`.

## Control Flow
`switch_mm()` extracts the ASID from `mm->context.id`, folds it into the high TTBR bits, writes TTBR0 as a 64-bit register pair, and issues an ISB. `set_pte_ext()` validates the low PTE word, clears valid for `L_PTE_NONE`, adjusts AP2 based on dirty/readonly state, stores the 64-bit PTE with `strd`, and cleans the PTE line on UP. `v7_ttb_setup` programs TTBCR with EAE and optionally split TTBR sizing, then writes TTBR1.

## State and Persistence Behavior
It mutates TTBR0/TTBR1, TTBCR, LPAE PTE memory, and PTE cache state. Static constants are consumed by ARMv7 setup.

## Dependencies and Integration Points
It integrates with ARMv7 LPAE builds, page-table definitions from `pgtable-3level.h`, SMP alternatives, endian configuration, and the main `proc-v7.S` setup path.

## Risks
Endian register pairing is critical for `mcrr` and `strd`. TTBR split logic depends on the relationship between `PHYS_OFFSET` and `PAGE_OFFSET`; wrong split setup can break secondary CPU identity mappings. 64-bit PTE permission updates must preserve all high attribute bits.

## Test Signals
Build ARMv7 LPAE kernels in UP/SMP and little/big endian where supported. Run high-memory, process, ASID, permission/NX, huge vmalloc/module, and secondary CPU boot tests. Inspect TTBR/TTBCR values when debugging early boot.
