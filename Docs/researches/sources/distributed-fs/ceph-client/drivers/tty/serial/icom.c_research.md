# sources/distributed-fs/ceph-client/drivers/tty/serial/icom.c

## Purpose
`icom.c` is the Linux serial-core driver for IBM iSeries ICOM PCI serial I/O adapters. It discovers supported IBM PCI device IDs, maps adapter registers, loads adapter firmware, allocates per-port coherent DMA buffers/status areas, and exposes active adapter ports as `ttyA*` UART devices through a `struct uart_driver`.

## Important APIs, types, and functions
Core types are `struct icom_adapter`, `struct icom_port`, `struct icom_regs`, `struct func_dram`, and `struct statusArea`. PCI integration is handled by `icom_pci_table`, `icom_probe()`, `icom_remove()`, and `icom_pci_driver`. Serial-core integration is `icom_uart_driver` plus `icom_ops`, including startup/shutdown, TX/RX, modem control, break, xchar, and termios callbacks. Firmware and adapter bring-up are concentrated in `load_code()`, `start_processor()`, `stop_processor()`, `icom_startup()`, and `icom_shutdown()`. Data movement is built around `get_port_memory()`, `free_port_memory()`, `icom_write()`, `xmit_interrupt()`, and `recv_interrupt()`.

## Control flow
Module init registers the UART driver, then the PCI driver. Probe enables the PCI device, requests BAR regions, enables memory/master/parity/SERR, applies adapter-specific PCI config writes, allocates an adapter, determines active ports, maps BAR0, requests a shared IRQ, allocates port DMA resources, and registers each active UART line. Opening a line increments the adapter `kref` and runs startup, which validates cable ID, may reload firmware, clears interrupt latches, and unmasks the correct global interrupt bits. Termios setup programs async format bytes, status masks, firmware command registers, RX descriptor address, TX restart address, and enables TX/RX. The IRQ handler demultiplexes V1/V2 adapter interrupt registers and dispatches active ports through RX/TX and modem handlers.

## State and persistence behavior
State lives in kernel memory and adapter DRAM only. Per-port state includes coherent descriptor/status pages, TX/RX buffers, next receive index, cached cable ID, status masks, and UART counters. Adapter state is on `icom_adapter_head` and is lifetime-managed by `kref`. Firmware is loaded through the kernel firmware API; no driver state is persisted to disk.

## Dependencies and integration points
Dependencies include PCI, DMA coherent allocation, firmware loading, MMIO accessors, interrupts, serial core, tty flip buffers, and tty kfifo TX queues. Externally it presents PCI driver `icom`, UART driver `icom`, devices named `ttyA`, and firmware requirements for `icom_call_setup.bin`, `icom_res_dce.bin`, and `icom_asc.bin`.

## Risks and test signals
Risks include missing/invalid firmware, adapter cable-ID changes, shared adapter lifetime during hot removal, descriptor endian/DMA address correctness, interrupt demux across inactive ports, and a static modem `old_status` shared across ports. Test probe/remove for supported adapter models, firmware failure/success, open/remove races, cable changes, TX wakeups, RX break/parity/frame/overrun handling, modem-control ioctls, and all supported baud-table entries.
