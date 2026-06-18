# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn20k.c

## Purpose

`cn20k.c` supplies CN20K-specific NIC operations. It implements new mailbox interrupt handling for AF/PF/VF and PF/VF channels, CN20K TC flower MCAM priority management, CN20K NPA aura/pool AQ initialization, CN20K SQ context initialization, and registers a CN20K `dev_hw_ops` table.

## Important APIs, Types, And Functions

- `cn20k_pfaf_mbox_intr_handler()` handles AF-to-PF up messages and AF replies.
- `cn20k_vfaf_mbox_intr_handler()` handles PF-to-VF notifications and replies.
- `cn20k_enable_pfvf_mbox_intr()`, `cn20k_disable_pfvf_mbox_intr()`, `cn20k_pfvf_mbox_intr_handler()`, and `cn20k_register_pfvf_mbox_intr()` manage four PF/VF mailbox interrupt vectors covering two mailbox banks and up to 96 VFs.
- TC helpers allocate/free MCAM entries, maintain priority ordering, and shift entries when possible.
- `cn20k_aura_aq_init()` and `cn20k_pool_aq_init()` program CN20K NPA AQ requests, including backpressure and page_pool setup.
- `cn20k_sq_aq_init()` programs CN20K NIX SQ contexts.
- `cn20k_hw_ops` selects CN20K mailbox, SQ, LMTST, refill, aura, and pool operations.
- `cn20k_init()` installs the ops table.

## Control Flow

PF/AF and VF/AF interrupt handlers read trigger bits, clear status, sync mailbox bounce buffers, inspect mailbox headers, queue the correct work item, and trace the interrupt. PF/VF registration allocates four `pf_irq_data` records, fills status register/start/mdev ranges by vector, names IRQs, requests IRQs with the selected hardware handler, and then enables interrupt masks.

TC allocation assigns hardware priority: rules with priority <=125 use that as hardware priority, otherwise PF/VF defaults 127/126. It allocates an MCAM entry relative to the current first TC entry unless using hardware priority. On add, the new node is inserted in priority order; if all entries up to the insertion point share the same key-width type, existing entries are shifted to preserve priority while saving MCAM space. Delete performs the inverse shift or frees the node's entry directly when mixed X2/X4 widths prevent shifting.

CN20K queue setup mirrors common/CN10K setup but uses CN20K mailbox request structures. Aura setup allocates a flow-control qmem cache line, configures count/limit/backpressure bpid, and uses a single `bpid` field rather than older split fields. Pool setup allocates stack qmem and creates a page_pool for RQ pools. `cn20k_init()` is a simple ops-table switch.

## State And Persistence

State includes `hw->pfvf_irq_devid[]`, dynamically allocated `pf_irq_data`, TC flow list entries and MCAM ids, NPA pool stack/fc/page_pool objects, and NIX SQ contexts. Hardware state persists in interrupt enable/status registers, NPC MCAM entries/counters, NPA aura/pool contexts, and NIX SQ contexts.

## Dependencies And Integration Points

The file depends on common NIC types, mailbox and trace helpers, CN10K LMT/refill helpers, TC flow-list helpers from `otx2_tc.c`, NPC install/free mailbox messages, DCB PFC mapping when enabled, page_pool, and CN20K register definitions from `otx2_reg.h`. PF/VF probe selects these ops for CN20K silicon.

## Risks

- PF/VF IRQ registration can leak already requested IRQs if a later vector request fails.
- Interrupt ranges use `mdevs = 96` for the second bank, so queue-work helpers must interpret start/count consistently.
- TC shifting only works when all affected entries have the same key-width type; mixed X2/X4 flows can reject insertion after resources were allocated.
- Delete shifting depends on list order and `list_next_entry()` before reaching the deleted node; edge cases need coverage.
- CN20K pool init returns page_pool errors without freeing previously allocated stack qmem.

## Test Signals

CN20K PF/VF probe with AF/PF and PF/VF mailbox traffic, >64 VF interrupt coverage, TC flower add/delete with priority shifts and mixed X2/X4 entries, MCAM allocation/free failure injection, RX/TX queue bring-up, DCB/PFC backpressure, page_pool allocation failure, and TX/RX traffic under CN20K ops are key signals.
