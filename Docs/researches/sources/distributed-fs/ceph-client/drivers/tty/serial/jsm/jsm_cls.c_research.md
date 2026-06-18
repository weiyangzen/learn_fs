# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_cls.c

## Purpose
`jsm_cls.c` implements `board_ops` for Digi Classic PCI serial adapters using Exar 16654-like UARTs. It programs Classic enhanced registers, handles the 8-bit interrupt poll path, manages FIFO thresholds and flow control, transfers RX data into JSM queues, drains tty TX data to the UART, and controls modem/break/receiver state.

## Important APIs, types, and functions
Flow-control programming is split across `cls_set_cts_flow_control()`, `cls_set_ixon_flow_control()`, `cls_set_no_output_flow_control()`, `cls_set_rts_flow_control()`, `cls_set_ixoff_flow_control()`, and `cls_set_no_input_flow_control()`. RX/TX movement uses `cls_copy_data_from_uart_to_queue()` and `cls_copy_data_from_queue_to_uart()`. Interrupt handling is `cls_intr()` and `cls_parse_isr()`. `cls_param()` programs baud, line control, interrupts, flow control, modem outputs, and B0 hangup behavior. `jsm_cls_ops` exports the operation table.

## Control flow
Classic probe selects these ops. Channel init disables interrupts, enters Exar enhanced access with LCR `0xbf`, enables enhanced controls, clears FIFOs, sets FIFO state flags, and clears stale LSR/MSR status. Board interrupts read `UART_CLASSIC_POLL_ADDR_OFFSET`; if pending, every active port is parsed. Channel parsing loops while the UART ISR reports work, servicing RX ready/timeouts, TX holding-register empty, and modem changes.

## State and persistence behavior
The Classic path mutates `jsm_channel` queue indices, flags, modem bytes, FIFO trigger levels, watermarks, and counters. Hardware state lives in Classic UART registers and the enhanced register set selected by LCR `0xbf`. State is volatile.

## Dependencies and integration points
It depends on `jsm.h`, serial register definitions, PCI logging, tty kfifo state, MMIO byte access, `jsm_input()`, and `jsm_check_queue_flow_control()`. `jsm_driver.c` selects `jsm_cls_ops` for Classic IDs.

## Risks and test signals
Risks include failing to restore LCR after enhanced-register access, RX overflow dropping oldest data, the noted Classic RX FIFO flush bug, suspicious DDSR handling through `uart_handle_dcd_change()`, and TX readiness relying on flags because FIFO counts are unreliable. Test Classic probe, baud/B0, CRTSCTS, IXON/IXOFF, disabled flow chars, RX/TX interrupts, modem deltas, break, queue overflow, and flush behavior.
