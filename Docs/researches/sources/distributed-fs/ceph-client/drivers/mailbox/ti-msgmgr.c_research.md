# sources/distributed-fs/ceph-client/drivers/mailbox/ti-msgmgr.c

## Purpose
`ti-msgmgr.c` implements the TI Message Manager and AM654 Secure Proxy mailbox controller. It maps SoC-specific queue/thread register windows into mailbox channels used by firmware protocols such as TI SCI.

## Important APIs, Types, and Functions
Important structures are `ti_msgmgr_desc`, `ti_msgmgr_valid_queue_desc`, `ti_queue_inst`, and `ti_msgmgr_inst`. Core routines are `ti_msgmgr_queue_get_num_messages()`, `ti_msgmgr_queue_is_error()`, `ti_msgmgr_queue_rx_data()`, `ti_msgmgr_queue_rx_interrupt()`, `ti_msgmgr_last_tx_done()`, `ti_msgmgr_send_data()`, `ti_msgmgr_queue_startup()`, `ti_msgmgr_queue_shutdown()`, `ti_msgmgr_of_xlate()`, `ti_msgmgr_queue_setup()`, `ti_msgmgr_suspend()`, `ti_msgmgr_resume()`, and `ti_msgmgr_probe()`.

## Control Flow, State, and Persistence
Probe selects a descriptor from OF match data, maps data/status/control resources, creates queue instances and mailbox channels, and registers the controller. For legacy Message Manager, valid queue/proxy pairs come from static descriptors; for Secure Proxy, each thread is exposed and direction is read at channel startup from the control register. TX writes message words in order and writes zero through the final register to complete transmission. RX reads every 32-bit register because the final read acknowledges the hardware queue. Suspend disables RX IRQs and marks RX channels polled so noirq TI SCI calls can still receive responses; resume restores IRQ mode. State is in queue direction, IRQ number, `rx_buff`, `polled_rx_mode`, mapped register pointers, and descriptor limits; persistence is the hardware FIFO/register state, not a filesystem format.

## Dependencies and Integration Points
The driver uses mailbox controller APIs, platform resource mapping by name, OF IRQ lookup, PM ops, `readl_poll_timeout_atomic()`, and `linux/soc/ti/ti-msgmgr.h` message objects. It binds `ti,k2g-message-manager` and `ti,am654-secure-proxy`.

## Risks and Test Signals
Risks include using sub-32-bit IO on queue registers, incorrect queue/proxy DT cells, Secure Proxy direction changes, shared IRQ spurious events, RX buffer lifetime across startup/shutdown, and suspend-time polling regressions. Tests should cover max and trailing-byte message sizes, invalid phandle args, TX credit exhaustion, RX IRQ and polled RX paths, suspend/resume with SCI traffic, and secure-proxy error/status masks.
