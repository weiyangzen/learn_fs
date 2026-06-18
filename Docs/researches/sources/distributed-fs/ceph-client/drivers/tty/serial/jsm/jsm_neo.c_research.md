# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_neo.c

## Purpose
`jsm_neo.c` implements `board_ops` for Digi Neo PCI/PCIe serial adapters using Exar 17C158-like UARTs. It handles Neo enhanced registers, FIFO burst transfer paths, 32-bit interrupt polling, auto hardware/software flow control, modem state, break handling, and PCI write posting flushes.

## Important APIs, types, and functions
Flow control is implemented by `neo_set_cts_flow_control()`, `neo_set_rts_flow_control()`, `neo_set_ixon_flow_control()`, `neo_set_ixoff_flow_control()`, `neo_set_no_input_flow_control()`, `neo_set_no_output_flow_control()`, and `neo_set_new_start_stop_chars()`. RX/TX movement uses `neo_copy_data_from_uart_to_queue()` and `neo_copy_data_from_queue_to_uart()`. Interrupt handling is `neo_intr()`, `neo_parse_isr()`, and `neo_parse_lsr()`. `neo_param()` programs termios. Control helpers include `neo_pci_posting_flush()`, FIFO flushes, receiver enable/disable, modem assertion, break and XON/XOFF helpers, UART init/off, and `jsm_neo_ops`.

## Control flow
Neo probe selects these ops. Channel init disables interrupts/features, enables ECB, clears FIFOs, reads stale status, marks FIFO enabled, and asserts modem outputs. Board interrupts lock the board, read the 32-bit poll register, use low eight bits to find pending ports, decode each port's three-bit interrupt type, clear the pending port bit, and dispatch RX timeout, RX line status, TX ready, or modem/status work. Unknown interrupt types are logged and ignored.

## State and persistence behavior
Neo state is held in `jsm_channel` flags, queue pointers, cached LSR, modem bytes, FIFO thresholds, watermarks, and counters. Hardware state is in EFR, FCTR, TX/RX FIFO trigger registers, start/stop character registers, LCR divisor latches, IER, MCR, and MSR. `neo_pci_posting_flush()` reads a device ID location to flush posted writes.

## Dependencies and integration points
It depends on `jsm.h`, serial register constants, tty kfifo APIs, PCI/device logging, MMIO byte/burst helpers, `jsm_input()`, and `jsm_check_queue_flow_control()`. `jsm_driver.c` selects `jsm_neo_ops`.

## Risks and test signals
Risks include Exar quirks: EFR zero-before-set, RX FIFO count off by three, small burst limits for IBM pSeries, bogus interrupt types, cached LSR races, queue overflow dropping oldest data, complex CRTSCTS/IXON/IXOFF transitions, and missing posting flushes. Test Neo PCI/PCIe probe, burst RX/TX, low-baud RX trigger, hardware and software flow control, RX errors, bogus interrupts, queue overflow, break, modem changes, FIFO flushes, and posting-sensitive writes.
