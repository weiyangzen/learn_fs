# sources/distributed-fs/ceph-client/drivers/usb/host/octeon-hcd.c

## Purpose
`octeon-hcd.c` is a complete Linux USB host-controller driver for Cavium/Marvell OCTEON USB2 hardware. Unlike the OHCI glue files nearby, it does not layer on a generic OHCI core; it implements its own `struct hc_driver` operations, private pipe/transaction scheduler, root-hub emulation, DMA/non-DMA data movement, and OCTEON register bring-up using the register definitions in `octeon-hcd.h`.

## Important APIs, types, and functions
Core private types are defined in this C file: `struct octeon_hcd` is the controller state stored in `usb_hcd.hcd_priv`; `struct cvmx_usb_pipe` models an endpoint pipe and its pending transaction list; `struct cvmx_usb_transaction` tracks a URB-backed transfer, current stage, retry count, byte counts, and ISO packet metadata. Supporting enums model USB speed, transfer type, direction, completion status, initialization flags, pipe flags, and split/control stages.

The Linux HCD interface is exported through `octeon_hc_driver`: `.irq = octeon_usb_irq`, `.start`, `.stop`, `.urb_enqueue`, `.urb_dequeue`, `.endpoint_disable`, `.get_frame_number`, `.hub_status_data`, `.hub_control`, and Octeon-specific DMA map/unmap hooks. Platform integration is through `octeon_usb_probe()`, `octeon_usb_remove()`, the `cavium,octeon-5750-usbc` OF match table, and module init/exit registration.

Hardware setup is concentrated in `cvmx_usb_initialize()`, `cvmx_fifo_setup()`, `cvmx_wait_tx_rx()`, `cvmx_usb_shutdown()`, `cvmx_usb_reset_port()`, `cvmx_usb_disable()`, and `cvmx_usb_get_status()`. Register access goes through `cvmx_usb_read_csr32()`, `cvmx_usb_write_csr32()`, and `USB_SET_FIELD32()`, which hide the OCTEON 32-bit CSR address swizzle.

The scheduling and transfer engine is split across `cvmx_usb_open_pipe()`, `cvmx_usb_submit_transaction()` and its typed wrappers, `cvmx_usb_schedule()`, `cvmx_usb_next_pipe()`, `cvmx_usb_find_ready_pipe()`, `cvmx_usb_start_channel()`, `cvmx_usb_start_channel_control()`, `cvmx_usb_poll()`, `cvmx_usb_poll_channel()`, `cvmx_usb_transfer_control()`, `cvmx_usb_transfer_bulk()`, `cvmx_usb_transfer_intr()`, `cvmx_usb_transfer_isoc()`, `cvmx_usb_complete()`, and `octeon_usb_urb_complete_callback()`. Non-DMA FIFO mode is handled by `cvmx_usb_poll_rx_fifo()`, `cvmx_usb_fill_tx_fifo()`, `cvmx_usb_fill_tx_hw()`, and `cvmx_usb_poll_tx_fifo()`.

## Control flow
Probe validates the device tree, reads the parent USBN clock frequency and reference-clock type, derives `CVMX_USB_INITIALIZE_FLAGS_*`, finds the USB block index from the MMIO resource, recovers an IRQ mapping for known broken DTs if necessary, coerces a 64-bit DMA mask, applies model-specific IOB priority tuning, allocates a `usb_hcd`, initializes `struct octeon_hcd`, selects usable hardware channels based on chip errata, calls `cvmx_usb_initialize()`, and registers the HCD with `usb_add_hcd()`.

URB enqueue links the URB to the endpoint, lazily opens a `cvmx_usb_pipe` in `ep->hcpriv`, computes endpoint type, speed, max packet, interval, high-speed split hub/port information, and then creates a transaction for bulk, interrupt, control, or isochronous URBs. ISO URBs get a private `cvmx_usb_iso_packet` array stored temporarily in `urb->setup_packet`. When a pipe receives its first transaction, it moves from `idle_pipes` to the appropriate `active_pipes[type]` list and scheduling is attempted.

Scheduling chooses ready pipes by priority: on SOF, isochronous then interrupt; always control then bulk. It assigns idle hardware channels, programs channel interrupt masks, DMA pointer registers, split registers, transfer-size registers, host-channel characteristics, and type-specific PID/control-stage details before enabling the channel. SOF interrupts are enabled only when future frame-gated work exists.

Interrupt handling enters `octeon_usb_irq()`, locks `usb->lock`, and calls `cvmx_usb_poll()`. Polling updates the extended frame counter, reads and clears `GINTSTS`, drains/fills FIFOs in non-DMA mode, reports root-hub changes on port/disconnect interrupts, scans `HAINT` for channel interrupts, calls `cvmx_usb_poll_channel()` for each active channel, and schedules more work. Channel polling computes bytes transferred from `HCTSIZ` and `HCCHAR`, updates PID toggles and retry state, classifies STALL/XACTERR/BABBLE/DATATGL/NYET/ACK/NAK/no-status cases, advances control/split stages, and eventually completes or retries the transaction.

Root hub operations are locally emulated for the single OCTEON port. `octeon_usb_hub_control()` answers hub descriptor/status requests, maps port status to Linux `USB_PORT_FEAT_*` and `USB_PORT_STAT_*` bits, drives port power through `HPRT.prtpwr`, resets the port through `cvmx_usb_reset_port()`, disables the port through `cvmx_usb_disable()`, and clears internal change state by refreshing `usb->port_status`.

## State and persistence behavior
All runtime state is volatile kernel memory owned by the HCD instance. The important persistent-across-interrupt state includes the idle channel bitmap, channel-to-pipe array, pipe lists, transaction lists, software Tx FIFOs, `frame_number`, `active_split`, cached `usbcx_hprt`, and cached root-hub `port_status`. Endpoint pipe pointers live in `usb_host_endpoint.hcpriv`; URB transaction pointers live in `urb->hcpriv`; ISO temporary packet arrays are temporarily stored in `urb->setup_packet`. There is no filesystem persistence.

Locking is centered on `octeon_hcd.lock`. Completion deliberately drops the spinlock around `usb_hcd_giveback_urb()` and reacquires it afterward. DMA mapping state is delegated to the USB core, except for temporary alignment buffers that are allocated before mapping and restored/freed after unmapping.

## Dependencies and integration points
The file depends on Linux USB HCD APIs, platform devices, OF properties, DMA mapping, IRQ mapping, kernel lists, spinlocks, and OCTEON platform helpers from `<asm/octeon/octeon.h>`. It uses register/unions from `octeon-hcd.h` and OCTEON CSR helpers such as `cvmx_read64_uint32()`, `cvmx_write64_uint32()`, `cvmx_read64_uint64()`, `cvmx_write64_uint64()`, `cvmx_write_csr()`, `cvmx_phys_to_ptr()`, `octeon_get_clock_rate()`, and `OCTEON_IS_MODEL()`.

Device-tree dependencies include a child compatible `cavium,octeon-5750-usbc` and parent USBN `clock-frequency` or `refclk-frequency`, plus `cavium,refclk-type` or `refclk-type`. Hardware integration is tightly tied to OCTEON USBN/USBC register layout and known CN31XX, CN5XXX, CN52XX, and CN56XX errata.

## Risks and edge cases
The driver has high concurrency and hardware-state risk because it maintains its own scheduler, split-transaction state machine, PID toggles, retry policy, and software FIFO handling. Non-DMA mode is especially timing-sensitive: RX FIFO polling must occur quickly enough to avoid overflow, and channel scheduling avoids the final quarter-frame. Split transaction handling uses frame arithmetic, an `active_split` singleton, retry rewinds, and special 188-byte ISO OUT chunks, all of which are regression-prone.

DMA and buffer handling is another risk area. The hardware transfers full 32-bit words, so unaligned-length buffers require temporary bounce buffers unless scatter-gather or pre-mapped DMA is used. ISO uses `urb->setup_packet` as private storage, which is compact but fragile if assumptions about ISO setup usage change. `cvmx_usb_submit_control()` uses setup `wLength` for OUT controls, and mistakes in direction/length interpretation would produce short or overrun transfers.

Error paths sometimes return `-1` instead of a specific errno after initialization/add failures. Probe error handling after successful hardware initialization but failed `usb_add_hcd()` does not call `cvmx_usb_shutdown()`. The interrupt path clears global interrupt status early, so misclassified events may be lost. Root-hub power and suspend semantics are limited; suspend is explicitly unsupported in hub control.

## Test signals
Useful validation includes boot/probe on supported OCTEON models with 12/24/48 MHz reference clocks and both crystal and external clock configurations; device enumeration at high, full, and low speed; full/low-speed devices behind high-speed hubs to exercise split control, bulk, interrupt, and ISO paths; high-speed bulk OUT NAK/PING behavior; unplug/replug and root-hub status change reporting; URB cancellation and endpoint disable while transfers are active; non-DMA CN31XX operation with FIFO interrupts; CN5XXX channel-3 avoidance; and DMA alignment tests with transfer lengths not divisible by four. Kernel dynamic debug around the `dev_dbg()` sites and USB core HCD traces are strong runtime observability signals.
