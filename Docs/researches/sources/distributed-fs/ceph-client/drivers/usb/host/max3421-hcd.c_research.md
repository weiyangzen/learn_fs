# sources/distributed-fs/ceph-client/drivers/usb/host/max3421-hcd.c

## Purpose
`max3421-hcd.c` is a USB host-controller driver for Maxim MAX3421E, a full-/low-speed USB host connected over SPI. Because SPI transactions can sleep, the driver serializes all chip I/O through a dedicated kernel thread and uses a spinlock-protected HCD state model for URB queues, root hub status, and endpoint metadata.

## Important APIs, Types, and Functions
- SPI I/O: `spi_rd8()`, `spi_wr8()`, `spi_rd_buf()`, and `spi_wr_buf()`.
- Transfer engine: `max3421_select_and_start_urb()`, `max3421_next_transfer()`, `max3421_ctrl_setup()`, `max3421_transfer_in()`, `max3421_transfer_out()`, `max3421_host_transfer_done()`, `max3421_recv_data_available()`, `max3421_handle_error()`, and `max3421_urb_done()`.
- Thread/IRQ/reset: `max3421_spi_thread()`, `max3421_irq_handler()`, `max3421_handle_irqs()`, `max3421_reset_hcd()`, and `max3421_reset_port()`.
- HCD/root hub/platform: `max3421_reset()`, `max3421_start()`, `max3421_urb_enqueue()`, `max3421_urb_dequeue()`, `max3421_endpoint_disable()`, `max3421_hub_status_data()`, `max3421_hub_control()`, `max3421_probe()`, and `max3421_remove()`.

## Control Flow
Probe validates SPI setup, IRQ, and platform/OF VBUS GPIO-output data, creates the HCD, allocates small DMA-safe SPI buffers, starts the SPI thread, registers the HCD, and requests the SPI IRQ. The thread configures PINCTL, waits for a supported chip revision, then loops: completes URBs, handles MAX3421 interrupts, selects new URBs when idle, and services todo bits for HCD reset, bus reset, unlink checks, and I/O-pin updates. The hard IRQ only wakes the thread and disables the IRQ until the thread is ready to sleep again.

The scheduler scans endpoint queues in periodic then non-periodic passes. It sets device address, speed/HUBPRE mode, packet state, and host-transfer command. Completion reads HRSL, handles errors or NAK/retry, reads IN FIFO data on RCVDAV, updates actual lengths, moves control transfers through setup/data/status, saves data toggles, unlinks the URB, and gives it back outside the spinlock.

Root hub control exposes one port, uses `port_status` lower 16 bits plus change bits in upper 16, powers VBUS through MAX3421 GPOUT pins, samples connection state from J/K bits, and performs reset through `HCTL.BUSRST`.

## State and Persistence Behavior
Runtime state is in `struct max3421_hcd`: SPI thread pointer, root hub state, port status/change mask, endpoint list, chip revision, frame number, current URB, scheduling pass, current packet length, interrupt-enable shadow, mode shadow, I/O pin shadows, todo bits, and optional debug counters. Per-endpoint state tracks packet state, retries, retransmit, NAK count, and last active frame. No persistent storage exists.

## Dependencies and Integration Points
The file integrates Linux SPI, USB HCD, OF/platform data (`maxim,vbus-en-pin`), kthreads, IRQs, and root hub polling (`HCD_FLAG_POLL_RH`). It maps MAX3421 register protocol and result codes into Linux USB core behavior.

## Risks and Test Signals
Risks include sleeping SPI operations accidentally called with locks held, endpoint disable freeing state while queued URBs remain, unsupported isochronous packet sizes above the 64-byte FIFO, NAK/retry behavior starving bulk endpoints, chip revision 0x12 retransmit workaround, incomplete bus suspend/resume returning `-1`, and remove not explicitly freeing tx/rx buffers after `usb_put_hcd()`. Test signals include SPI IRQ/thread wake behavior, attach/detach and low-speed detection, VBUS GPOUT polarity, control enumeration, bulk IN/OUT with zero packets, interrupt interval scheduling, NAK/error/retry injection, unlink of current and queued URBs, and OF/platform-data validation failures.
