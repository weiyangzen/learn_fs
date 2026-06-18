# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-gcu.h

Purpose: defines the userspace-visible ABI for the PXA3xx GCU misc driver: shared memory layout, buffer sizing, ABI magic, batch size, and ioctl numbers.

Important APIs/types/functions: `PXA3XX_GCU_BUFFER_WORDS` sizes the shared ring-buffer command area to almost 256 KiB. `PXA3XX_GCU_SHARED_MAGIC` identifies the ABI version and is set by kernel reset for userspace validation. `PXA3XX_GCU_BATCH_WORDS` limits a submitted batch to 8192 32-bit words. `struct pxa3xx_gcu_shared` contains the command ring, `hw_running`, the physical ring address, statistic counters (`num_words`, `num_writes`, `num_done`, `num_interrupts`, `num_wait_idle`, `num_wait_free`, `num_idle`), and `magic`. IOCTLs are `PXA3XX_GCU_IOCTL_RESET` and `PXA3XX_GCU_IOCTL_WAIT_IDLE`.

Control flow: userspace mmaps the shared area described by this header, validates `magic`, observes `hw_running` and counters, submits command data with `write`, and uses ioctls for reset or idle synchronization. The driver writes `buffer_phys` and `magic` during `pxa3xx_gcu_reset`, increments counters during writes/waits/IRQs, and uses the ring buffer to chain DMA batch buffers.

State and persistence: this header defines shared kernel/userspace state but does not allocate it. Runtime state persists in coherent DMA memory until reset, driver removal, or device reset. Counters are diagnostic, not transactional, and comments in the C file indicate not all updates are atomic.

Dependencies and integration: included by `pxa3xx-gcu.c` and expected by the matching DirectFB or other userspace client. It uses Linux integer types and `_IO` ioctl encoding via the C file's includes.

Risks: changing `struct pxa3xx_gcu_shared`, buffer sizing, or ioctl values breaks userspace unless `PXA3XX_GCU_SHARED_MAGIC` is bumped. `unsigned long buffer_phys` is ABI-width dependent, which matters for 32-bit versus 64-bit consumers. The shared flags and counters are not a complete synchronization contract by themselves.

Test signals: compile the kernel driver and userspace client against the same header, verify `magic`, mmap size, ioctl numbers, and batch-size rejection. ABI tests should check 32-bit userspace assumptions, counter monotonicity, and reset reinitialization of `hw_running`, `buffer_phys`, and statistics.
