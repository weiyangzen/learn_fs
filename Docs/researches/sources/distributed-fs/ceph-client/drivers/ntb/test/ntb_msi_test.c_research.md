# sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_msi_test.c

## Purpose
Provides a debugfs test client for the NTB MSI helper. It allocates local MSI IRQs, shares their trigger descriptors through scratchpads, learns peer descriptors after doorbell notifications, and exposes debugfs knobs to trigger peer interrupts and read occurrence counts.

## Important APIs, Types, And Functions
- `struct ntb_msit_ctx` stores the NTB device, setup work, local ISR contexts, and flexible peer array.
- `struct ntb_msit_isr_ctx` tracks an allocated IRQ, descriptor, and occurrence count.
- `struct ntb_msit_peer` tracks peer index, descriptor array, IRQ count, and completion.
- `ntb_msit_setup_work()` sets MSI MWs, requests up to `num_irqs` MSI IRQs, writes descriptors to scratchpads, publishes count in scratchpad 0, and rings peers.
- `ntb_msit_db_event()` reads peer descriptor counts and descriptor scratchpads after doorbell events.
- Debugfs files expose peer `trigger`, `ready`, `count`, `port`, local `port`, and per-IRQ occurrence counters.

## Control Flow
Probe validates peer count and scratchpad capacity, initializes scratchpad 0 to `-1`, unmasks peer doorbells, initializes the MSI helper, allocates context, creates debugfs, sets NTB context callbacks, and enables link. Link-up schedules setup work. Setup work programs MSI MWs and publishes descriptors. Doorbell events copy peer descriptors and complete peer readiness. Writing a peer `trigger` debugfs file calls `ntb_msi_peer_trigger()` with the selected descriptor.

## State And Persistence
Local IRQ descriptors live in `isr_ctx`. Peer descriptors are heap allocated and replaced on each doorbell event. Scratchpads persist the descriptor exchange protocol: count in slot 0, then address offset/data pairs. Occurrence counts are volatile counters incremented by the ISR.

## Dependencies And Integration Points
Depends on `ntb_msi_init()`, `ntb_msi_setup_mws()`, `ntbm_msi_request_irq()`, scratchpads, doorbells, debugfs, and NTB link callbacks.

## Risks And Edge Cases
- Uses scratchpad indices `2 * i + 1/2`; `num_irqs` must fit `2 * num_irqs + 1`.
- `ntb_msit_db_event()` iterates over all bits in a 64-bit mask and indexes `peers[peer]`; valid doorbell masks must match actual peer count.
- Descriptor updates are not separately synchronized with debugfs trigger reads; stale descriptor arrays are possible during link churn.
- Probe contains a redundant `if (!nm->isr_ctx)` after allocation already succeeded.

## Test Signals
After link-up, debugfs peer `ready` should complete, `count` should equal published IRQ count, writing `trigger` should increment the peer's `irqN_occurrences`, and descriptor-change logs should be followed by successful peer triggers.
