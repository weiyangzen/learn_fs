# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/irq.c

## Purpose
This file handles HabanaLabs CQ, EQ, user, decoder, and EQ-error interrupts, turning hardware queue entries into completion work, event work, timestamp updates, wait-fence completions, and reset actions.

## Important APIs, Types, And Functions
`hl_irq_handler_cq()` drains completion queues. `hl_irq_handler_eq()` drains event queues. `hl_irq_user_interrupt_handler()` handles CQ/decoder user interrupts. `hl_irq_user_interrupt_thread_handler()` handles TPC/unexpected interrupts. `hl_irq_eq_error_interrupt_thread_handler()` triggers reset. Queue lifecycle functions are `hl_cq_init/fini/reset()` and `hl_eq_init/fini/reset/dump()`.

## Control Flow
CQ handling loops on ready entries, uses `dma_rmb()`, dispatches completion by CS or by job shadow index, clears ready, advances CI, and returns free slots. EQ handling validates optional indices, copies entries to work items, queues ASIC event handling, clears ready, advances CI, and updates firmware-visible CI. User interrupts complete waiters first, then timestamp registrations, deferring object puts to workqueue context.

## State And Persistence
The file updates CQ/EQ CI, free-slot counters, CS/job timestamps, wait fences, timestamp buffer contents, and timestamp cleanup pools. CQ/EQ memory is allocated from coherent or CPU-accessible DMA pools and cleared on reset.

## Dependencies And Integration Points
It relies on queue shadow state from `hw_queue.c`, CS/job work structs, ASIC event handlers, workqueues, reset logic, mmap buffer and CB refcounting, and user interrupt registration state.

## Risks
Interrupt context cannot sleep, so timestamp cleanup deferral is critical. Stale queue entries after reset can schedule invalid work if memory is not cleared. EQ work allocation failure can drop events. Free-node pool fallback uses GFP_ATOMIC and can fail.

## Test Signals
Test per-CS/per-job completion, disabled-device interrupts, reset queue clearing, EQ index mismatch, EQ work allocation failure, timestamp cleanup, wait completions, TPC reset, EQ hard reset, and init/fini paths.
