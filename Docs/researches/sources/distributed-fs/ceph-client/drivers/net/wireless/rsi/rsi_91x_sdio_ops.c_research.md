# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_sdio_ops.c

## Purpose
This file contains SDIO-specific runtime operations for master register window setup, RX interrupt processing, slave-register initialization, hardware buffer-status tracking, and TX scheduler timeout selection.

## Important APIs, Types, and Functions
Public functions are `rsi_sdio_master_access_msword`, `rsi_sdio_rx_thread`, `rsi_init_sdio_slave_regs`, `rsi_sdio_check_buffer_status`, and `rsi_sdio_determine_event_timeout`. Internal helpers are `rsi_process_pkt` and `rsi_rx_handler`.

## Control Flow
`rsi_sdio_rx_thread` waits for the SDIO interrupt event and invokes `rsi_rx_handler` until shutdown. The handler reads `RSI_FN1_INT_REGISTER`, stores it in `adapter->interrupt_status`, handles buffer-available interrupts by refreshing queue status and waking the TX thread, handles firmware-assert interrupts by reading firmware status and marking the card not ready, handles packet-pending interrupts by reading the block count and packet buffer, and acknowledges unknown residual interrupts. Packet reads call `rsi_sdio_host_intf_read_pkt` followed by shared `rsi_read_pkt`. Slave-register init writes optional read delay, high-speed mode, read start level, and FIFO controls. Buffer-status checks update management/data full flags and return `QUEUE_FULL` or `QUEUE_NOT_FULL` to the common QoS scheduler.

## State and Persistence Behavior
This file mutates `adapter->interrupt_status`, `common->fsm_state`, `dev->rx_info` counters/flags, `dev->buff_status_updated`, and `dev->write_fail`. It also programs SDIO slave registers that persist in the device until reset. Timeout behavior becomes polling-like every 2 ms when the device reports data buffers full.

## Dependencies and Integration Points
It depends on register accessors and ACK helpers implemented in `rsi_91x_sdio.c`, common packet parsing in `rsi_read_pkt`, common TX scheduling through `common->tx_thread.event`, and queue IDs from RSI descriptors. Debugfs can expose some RX counters through the private SDIO state.

## Risks
The RX handler loops until it sees zero interrupt status; missed ACKs or a stuck interrupt can keep the RX thread active. Packet length is inferred from interrupt bits or `SDIO_RX_NUM_BLOCKS_REG`, so corrupt status can force invalid reads. Buffer-full state uses a static throttle counter shared across adapters. Firmware asserts only mark the FSM not ready; recovery depends on higher-level reset/disconnect. `rsi_sdio_rx_thread` increments `thread_done` on exit after the killer already increments it, which is harmless but unusual.

## Test Signals
Test interrupt cases for status zero, packet pending, buffer available, firmware assert, and unknown bits; RX block-count edge cases; queue-full transitions for management/data queues; TX scheduler wakeups when buffers clear; slave-register init errors; and sustained RX/TX under SDIO buffer pressure.
