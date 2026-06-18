<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/interrupt.c

Purpose: provides common interrupt-thread logic for reading firmware messages, dispatching HBM/control/data packets, draining write queues, completing callbacks, and detecting protocol stalls/timeouts. Hardware backends call these routines after platform-specific IRQ acknowledgment.

Important APIs and functions: exported functions are `mei_irq_compl_handler()`, `mei_irq_read_handler()`, `mei_irq_write_handler()`, `mei_schedule_stall_timer()`, and `mei_timer()`. Local helpers validate message headers, discard unread payloads, route client messages, process extended vtag/GSC headers, send disconnect responses and flow-control requests, and handle connect/disconnect timeouts.

Control flow: `mei_irq_read_handler()` reads a MEI header if not already cached, validates reserved bits and minimum extended/DMA lengths, reads extended metadata and DMA length slots, dispatches HBM packets to `mei_hbm_dispatch()`, routes client packets by host/ME address, discards fixed-address or power-down orphan messages, and resets cached header state before recounting slots. `mei_cl_irq_read_msg()` attaches received fragments to pending read callbacks, validates vtag/GSC extended headers, reads from DMA ring or hardware slots, completes callbacks when `msg_complete` is set, and requests autosuspend on partial messages. `mei_irq_write_handler()` acquires the host buffer, completes write-waiting callbacks, then drains control writes and normal writes in order. `mei_timer()` handles HBM init stalls and per-client connect/disconnect timeouts.

State and persistence: mutates volatile callback lists (`write_waiting_list`, `ctrl_wr_list`, `write_list`, `rd_pending`, completion list), cached read headers, per-client read buffers, vtags, GSC ext headers, status fields, timer counters, and waitqueues. No persistent storage.

Dependencies and integration: depends on `hbm.h`, `client.h`, DMA ring helpers, runtime PM, kthreads/workqueues, common hardware read/write wrappers, and hardware backend IRQ threads.

Risks: malformed firmware headers can trigger resets; some paths return `-EBADMSG`, `-ENODATA`, `-ERANGE`, or `-EPROTO` to backend IRQ threads. Extended-header parsing depends on validated dword sizes and can allocate per-callback GSC header memory. Missing read callbacks are tolerated only for fixed-address clients. The write path assumes callbacks are correctly queued by client code and can return `-EMSGSIZE` when hardware buffer space is insufficient.

Test signals: interrupt-driven read/write under userspace traffic, fragmented multi-packet reads, vtag mismatch rejection, GSC extended-header handling, DMA-ring reads, fixed-address orphan discard, flow-control issuance, connect timeout behavior with and without disconnect-on-timeout support, and reset on corrupted headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/interrupt.c -->
