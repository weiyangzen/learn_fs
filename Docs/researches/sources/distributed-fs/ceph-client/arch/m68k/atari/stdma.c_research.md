# sources/distributed-fs/ceph-client/arch/m68k/atari/stdma.c

Purpose: shared arbitration layer for the Atari ST-DMA interrupt/chip used by floppy, ACSI, IDE interrupt routing, and Falcon SCSI.

Important APIs are `stdma_try_lock()`, `stdma_lock()`, `stdma_release()`, `stdma_is_locked_by()`, `stdma_islocked()`, and `stdma_init()`. A caller acquires the lock with an IRQ handler and data cookie; the common `stdma_int()` invokes that registered handler when `IRQ_MFP_FDC` fires.

State includes `stdma_locked`, `stdma_isr`, `stdma_isr_data`, and wait queue `stdma_wait`. Lock/unlock operations disable local IRQs around state changes. `stdma_lock()` sleeps uninterruptibly until `stdma_try_lock()` succeeds, because users can involve filesystem buffers.

Dependencies include Atari ST-DMA hardware context, `IRQ_MFP_FDC`, Linux wait queues, request_irq, and exported symbols for storage drivers. Integration is initialized from `atari_init_IRQ()`.

Risks and test signals: interrupt handlers must release through their mainline flow; calling `stdma_lock()` from IRQ context is forbidden; `stdma_islocked()` requires interrupts disabled for stable interpretation. Test concurrent floppy/SCSI/ACSI access, lock contention wakeups, handler dispatch, and release-on-error paths in client drivers.
