<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rmu.c

Purpose: Implements Freescale MPC85xx/MPC86xx RapidIO RMU support for outbound/inbound mailbox messages, inbound/outbound doorbells, port-write reception, and message-unit error cleanup.

Important APIs/types/functions: Defines RMU register layouts `rio_msg_regs`, `rio_dbell_regs`, `rio_pw_regs`, descriptor/ring structures, and `struct fsl_rmu`. Main entry points are `fsl_rio_setup_rmu()`, `fsl_rio_doorbell_init()`, `fsl_rio_port_write_init()`, `fsl_rio_pw_enable()`, `fsl_rio_doorbell_send()`, `fsl_open_outb_mbox()`, `fsl_close_outb_mbox()`, `fsl_add_outb_message()`, `fsl_open_inb_mbox()`, `fsl_close_inb_mbox()`, `fsl_add_inb_buffer()`, and `fsl_get_inb_message()`. Interrupt paths are `fsl_rio_tx_handler()`, `fsl_rio_rx_handler()`, `fsl_rio_dbell_handler()`, and `fsl_rio_port_write_handler()`.

Control flow: Setup allocates `struct fsl_rmu`, derives the message-unit register window from the device tree, maps TX/RX IRQs, and attaches the handle to the RapidIO master-port private data. Mailbox open paths validate power-of-two ring sizes, allocate coherent descriptor/message rings, program enqueue/dequeue pointers, request IRQs, and enable the message unit. TX enqueue copies the user buffer to the current DMA buffer, fills a descriptor, advances the hardware enqueue pointer, and rotates the software slot. RX delivery is interrupt-driven: the IRQ callback notifies the RapidIO core, while `fsl_get_inb_message()` copies from the inbound DMA ring to a client buffer and re-enables message interrupts. Doorbell and port-write handlers parse hardware queues, dispatch matching callbacks, acknowledge status bits, and schedule deferred port-write processing via workqueue.

State and persistence: Long-lived state includes coherent TX/RX rings, per-slot physical buffers, ring indexes, interrupt numbers, global doorbell and port-write objects declared in `fsl_rio.h`, FIFO/workqueue state for port writes, and status/error counters. Register state is persistent hardware state: message mode/status registers, queue pointers, doorbell masks, port-write queue base registers, and link/error enables. Doorbell send is serialized by `fsl_rio_doorbell_lock`; port-write FIFO extraction uses `kfifo_out_spinlocked()`.

Dependencies and integration points: Depends on Linux RapidIO core callbacks/resources, Freescale RapidIO globals from `fsl_rio.h`, DMA-coherent memory, OF address/IRQ parsing, workqueues, kfifo, and big-endian MMIO helpers. It integrates with board-level RapidIO setup that supplies `rio_regs_win`, `rmu_regs_win`, `dbell`, and `pw`.

Risks: Hardware queue processing comments acknowledge that RX, doorbell, and port-write handlers process only one queued event rather than draining until empty. Several paths assume globally initialized RapidIO windows and objects. Mailbox close frees descriptor rings but not every per-slot outbound DMA buffer allocated in open. Error recovery mostly clears status without rebuilding queues. The code casts DMA addresses to `u32`, so platforms with addresses beyond 32 bits would be fragile.

Test signals: Useful signals include RapidIO enumeration on MPC85xx/MPC86xx, inbound/outbound mailbox loopback, doorbell delivery across multiple ports and resource ranges, port-write FIFO overflow and transaction-error tests, queue-full/error interrupt injection, IRQ teardown/reopen cycles, DMA leak checking, and lockdep around doorbell and port-write paths.

Source read size: 1107 lines, 29398 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rmu.c -->
