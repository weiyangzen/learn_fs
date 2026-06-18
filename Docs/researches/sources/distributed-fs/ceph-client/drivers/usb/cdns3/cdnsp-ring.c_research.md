# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ring.c

Purpose: implements the CDNSP command, event, endpoint transfer, and stream ring engine. The complete 2504-line file was read. It owns TRB enqueue/dequeue movement, doorbells, command submission, transfer queueing for all endpoint types, event handling, cancellation, stream NRDY handling, port-status handling, bounce cleanup, and IRQ dispatch.

Important APIs/types/functions: `cdnsp_trb_virt_to_dma()`, `cdnsp_last_trb_on_seg()`, `cdnsp_last_trb_on_ring()`, `cdnsp_inc_deq()`, `cdnsp_ring_cmd_db()`, `cdnsp_ring_doorbell_for_active_rings()`, `cdnsp_remove_request()`, `cdnsp_thread_irq_handler()`, `cdnsp_irq_handler()`, `cdnsp_queue_bulk_tx()`, `cdnsp_queue_ctrl_tx()`, `cdnsp_cmd_stop_ep()`, `cdnsp_queue_isoc_tx()`, and command helpers for slot/address/reset/configure/stop/set-dequeue/reset-ep/halt/force-header.

Control flow: queue paths prepare room, append TDs, write TRBs while withholding first-TRB ownership, then publish the first TRB and ring a doorbell. Hard IRQ acknowledges controller events and wakes the thread. Threaded IRQ drains owned event TRBs, dispatches command, port, transfer, setup, NRDY, and controller events, then updates ERST dequeue. Completion computes actual/status, advances dequeue, unmaps bounce buffers, and gives requests back.

State and persistence: persistent ring state includes segment pointers, enqueue/dequeue pointers, cycle bits, free counts, TD lists, per-stream active/rejected/doorbell counters, endpoint skip flags, event dequeue state, and command status/TRB pointers. Hardware-visible TRB memory persists until consumed or cleaned.

Dependencies/integration: Linux SG/DMA/delay/IRQ helpers, CDNSP trace/debug, shared structures, EP0 setup, gadget giveback, memory-managed rings/streams, command wait logic, and port reset/suspend/resume callbacks.

Risks: cycle-bit/link-TRB handling is fragile; cancellation must choose set-dequeue vs no-op conversion correctly; missed isoc service uses `pep->skip`; stream doorbells are limited and depend on PRIME/REJECT events; bounce-buffer direction and SG lengths are subtle; command timeout marks controller dying.

Test signals: bulk SG across 64 KiB boundaries, zero-length/ZLP cases, streams with PRIME/REJECT, isoc underrun/overrun/missed-service, request dequeue while running/disconnecting, ring expansion, halt/reset, command timeout injection, event-ring wrap, port transitions, and TRB trace validation.
