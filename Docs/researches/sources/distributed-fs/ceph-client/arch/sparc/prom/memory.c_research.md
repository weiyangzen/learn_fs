# sources/distributed-fs/ceph-client/arch/sparc/prom/memory.c

Purpose: gathers SPARC32 physical memory availability from PROM and populates `sp_banks`.

Important APIs/functions: exposes `prom_meminit()`. Helpers are `prom_meminit_v0()`, `prom_meminit_v2()`, and `sp_banks_cmp()`.

Control flow: V0 walks the ROM vector available-memory linked list; V2/V3 finds the `memory` node and reads its `available` property into register entries. `prom_meminit()` sorts discovered banks by base address, writes a sentinel with zero size, and page-aligns bank sizes downward.

State and persistence: writes global boot-time `sp_banks` memory-bank array used by early MM setup. No persistent storage.

Dependencies and integration points: called by SPARC32 `prom_init()` before `srmmu_paging_init()` uses `sp_banks` to compute memory and create mappings.

Risks: fixed local register array limits parsed entries. Incorrect sorting or missing sentinel can make boot memory setup overrun or mis-map RAM. Page-size truncation discards unaligned tail bytes.

Test signals: boot PROM V0/V2/V3 with multiple banks, out-of-order banks, small unaligned bank tails, and no/invalid memory node behavior.
