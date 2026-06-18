# sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can.c

## Purpose
`m_can.c` is the shared SocketCAN class driver for Bosch M_CAN controller IP. It provides the common netdev lifecycle, register programming, Message RAM layout handling, RX/TX processing, CAN state/error reporting, ethtool coalescing, power-management helpers, and exported class registration functions used by platform, PCI, and SPI peripheral wrappers.

## Important APIs, Types, And Functions
- Register definitions and bit masks cover the M_CAN core release, CCCR, bit timing, interrupt, FIFO, Message RAM, timestamp, error counter, and protocol status registers.
- `m_can_read()`, `m_can_write()`, `m_can_fifo_read()`, `m_can_fifo_write()`, and `m_can_txe_fifo_read()` dispatch through `struct m_can_ops`, allowing the common driver to work with MMIO or SPI/regmap transports.
- RX path functions include `m_can_read_fifo()`, `m_can_do_rx_poll()`, `m_can_rx_handler()`, and `m_can_poll()`.
- Error handling is split across `m_can_handle_lost_msg()`, `m_can_handle_lec_err()`, `m_can_handle_state_change()`, `m_can_handle_state_errors()`, `m_can_handle_protocol_error()`, and `m_can_handle_bus_errors()`.
- TX path functions include `m_can_start_tx()`, `m_can_tx_handler()`, `m_can_start_xmit()`, `m_can_echo_tx_event()`, `m_can_finish_tx()`, and peripheral workqueue helpers.
- Configuration functions include `m_can_cccr_update_bits()`, `m_can_config_enable()`, `m_can_init_ram()`, `m_can_set_bittiming()`, `m_can_chip_config()`, `m_can_start()`, and `m_can_stop()`.
- Exported APIs are `m_can_check_mram_cfg()`, `m_can_class_get_clocks()`, `m_can_class_allocate_dev()`, `m_can_class_free_dev()`, `m_can_class_register()`, `m_can_class_unregister()`, `m_can_class_suspend()`, and `m_can_class_resume()`.

## Control Flow
Wrappers allocate an `m_can_classdev` with `m_can_class_allocate_dev()`, fill clock/IRQ/transport fields, then call `m_can_class_register()`. Registration computes a safe TX FIFO size, gets reset control, powers/clocks the controller, optionally adds RX offload for peripherals, sets up an hrtimer for polling or interrupt coalescing, probes the core release, initializes CAN capabilities, registers the candev, reads transceiver configuration, and powers the controller back down until open.

Open powers the PHY, resumes clocks, deasserts reset, opens the candev, enables NAPI or peripheral RX offload, requests the interrupt, runs `m_can_start()`, and starts the queue. Start programs Message RAM, filters, TX/RX FIFOs, CCCR modes, bit timing, timestamps, and interrupts, then clears `CCCR_INIT` to enter normal mode.

RX processing is interrupt or hrtimer driven. The interrupt handler reads and acknowledges `M_CAN_IR`, handles edge-triggered wrappers by looping until IR is observed clear, updates coalescing, dispatches RX/error work to NAPI for non-peripherals or directly to the offload path for peripherals, and handles TX completion. NAPI combines latched `irqstatus` with current IR and calls `m_can_rx_handler()`.

TX first reserves a logical in-flight slot under `tx_handling_spinlock`. Version 3.0 uses a single TX buffer and `IR_TC`; newer versions use TX FIFO/queue plus TX event FIFO message markers. Peripheral chips queue TX work to an ordered workqueue and may batch `TXBAR` submission until `netdev_xmit_more()` or the configured coalescing threshold.

Suspend stops or partially leaves the chip running for wake-capable devices, updates pinctrl state, clocks down the device, and marks state sleeping. Resume restores pinctrl, clocks, interrupts, optional wrapper init, controller state, and queue attachment.

## State And Persistence
Runtime state lives in `struct m_can_classdev`: CAN core state, NAPI/offload state, active interrupt mask cache, coalescing values, TX FIFO indices and in-flight count, workqueue operations, MRAM layout, reset/clock handles, transceiver, hrtimer, and wake pinctrl. Message RAM contents are initialized at start and then used as hardware queues. There is no on-disk persistence.

## Dependencies And Integration Points
This file depends on the SocketCAN core, CAN FD helpers, RX offload, NAPI, hrtimers, ethtool, runtime PM, reset, clocks, PHY, pinctrl, fwnode/device-tree properties, and wrapper-provided `m_can_ops`. The integration contract is that wrappers must provide valid register/FIFO operations, `bosch,mram-cfg`, clock frequency, IRQ/polling mode, and peripheral flags before registration.

## Risks And Edge Cases
- `m_can_cccr_update_bits()` refuses many configuration writes when not in init mode; wrappers that call class APIs with bad power/reset sequencing can fail with `-EBUSY`.
- Message RAM configuration is firmware-supplied; bad offsets/counts can corrupt hardware queues unless wrapper-specific size checks such as `m_can_check_mram_cfg()` are used.
- TX accounting depends on TX event FIFO message markers matching echo skb slots.
- Peripheral chips perform bus access from a workqueue, so stop/close paths must destroy the workqueue after TX operations are quiesced.
- Coalescing settings are only accepted while stopped and must stay within RX FIFO/TX FIFO/TX event FIFO capacities.
- `m_can_start()` ignores the return value of `m_can_start()` in `m_can_set_mode()` before waking the queue, so restart error propagation is limited there.
- Edge-triggered IRQ wrappers require the IR drain loop to avoid missing a later edge.

## Test Signals
Use loopback, listen-only, one-shot, CAN FD, CAN FD non-ISO, BERR reporting, bus-off/restart, interrupt coalescing, polling mode, RX overflow, protocol error injection, suspend/resume with and without wakeup, runtime PM, and TX FIFO saturation tests. Also validate that MRAM layout errors are rejected and that ethtool coalescing rejects invalid active or out-of-range settings.
