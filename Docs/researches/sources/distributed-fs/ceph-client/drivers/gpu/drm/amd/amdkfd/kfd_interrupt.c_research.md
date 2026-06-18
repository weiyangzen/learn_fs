# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_interrupt.c

Purpose: provides the shared KFD interrupt buffering and deferred-processing framework. KGD/amdgpu ISR code asks KFD whether an IH entry is wanted; wanted entries are copied into a per-node FIFO and processed later on a high-priority workqueue.

Important APIs/types/functions: `kfd_interrupt_init` allocates `node->ih_fifo`, creates a shared `KFD IH` workqueue if necessary, initializes `node->interrupt_lock`, sets up `node->interrupt_work`, and publishes `interrupts_active`. `kfd_interrupt_exit` stops new interrupt work and frees the FIFO. `enqueue_ih_ring_entry` copies entries into the FIFO with overflow warning. `interrupt_wq` drains entries and invokes the generation-specific `event_interrupt_class->interrupt_wq`. `interrupt_is_wanted` calls the generation-specific ISR filter.

Control flow: device init calls `kfd_interrupt_init`; it allocates a fixed FIFO sized for 16,384 IH entries times the hardware entry size and uses `smp_wmb` before interrupts become visible. ISR-side code calls `interrupt_is_wanted`, then `enqueue_ih_ring_entry` and schedules `node->interrupt_work` elsewhere in the driver. The worker repeatedly obtains a linear FIFO pointer, passes it to the ASIC-specific workqueue decoder, then skips the consumed bytes. If it spends more than one second in one run, it requeues itself to avoid soft-lockup warnings.

State and persistence: owns per-node FIFO memory, `interrupts_active`, spinlock initialization, and work item registration. There is no persistent disk state; loss is possible when the FIFO overflows because hardware provides no back-pressure or acknowledgment.

Dependencies/integration: depends on Linux `kfifo`, workqueues, spinlocks, and `struct kfd_event_interrupt_class` installed in `node->kfd->device_info`. It is the bridge between amdgpu ISR context and KFD scheduler/event/debug processing.

Risks: comments assume single reader/writer and non-reentrant enqueue/dequeue. FIFO overflow loses events. `kfd_interrupt_exit` frees the FIFO after disabling interrupts but does not itself flush queued work, so teardown ordering elsewhere must guarantee no use-after-free. Test signals include FIFO overflow warnings, worker rescheduling under interrupt storms, init/exit race tests, and generation-specific interrupt callback invocation.
