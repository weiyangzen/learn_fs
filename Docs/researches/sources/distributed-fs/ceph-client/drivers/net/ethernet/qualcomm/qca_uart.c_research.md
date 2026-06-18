<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_uart.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_uart.c

## Purpose
`qca_uart.c` implements a QCA7000 Ethernet-over-UART netdev using the serdev framework and the shared QCA7K framing protocol.

## Important APIs, Types, and Functions
- `struct qcauart` stores netdev, spinlock, TX work, serdev, framing handle, RX skb, and TX buffer pointers/counts.
- `qca_tty_receive()` decodes received serial bytes through `qcafrm_fsm_decode()` and submits completed Ethernet frames.
- `qcauart_netdev_xmit()` builds a framed/padded packet in a preallocated TX buffer, writes as much as serdev accepts, stops the netdev queue, and records remaining bytes.
- `qcauart_transmit()` continues writing pending TX bytes from workqueue context and wakes the queue when complete.
- `qca_uart_probe()` allocates/registers the netdev, configures serdev callbacks, baud rate, flow control, MAC address, carrier state, and framing FSM.

## Control Flow
Probe opens the serdev, sets baud and flow control, then registers the netdev. Netdev open starts the queue. TX stops the queue until the work item, triggered by serdev write wakeups, drains the pending buffer. RX callback processes incoming bytes immediately and may allocate a new skb after each completed frame. Remove unregisters netdev, closes serdev, cancels TX work, and frees the netdev.

## State and Persistence
Per-device state is netdev private data. TX state persists in `tx_buffer`, `tx_head`, and `tx_left` across partial serdev writes. RX framing state persists across receive callbacks. Carrier is set on at probe because UART has no SPI-style sync.

## Dependencies and Integration Points
Depends on serdev, OF MAC/current-speed properties, netdev APIs, and `qca_7k_common`. DT compatible is `"qca,qca7000"`, shared with the SPI binding but used on a serdev bus.

## Risks and Edge Cases
- TX uses one buffer and stops the queue, so only one packet can be in flight.
- `tx_packets` increments when TX buffer drains, while `tx_bytes` increments only by the first write amount, not necessarily the full framed or payload length.
- RX path must set `rx_skb->dev`; the initial skb relies on allocation helper context and subsequent protocol assignment.
- No explicit carrier/sync validation exists for UART beyond serial open.
- Spinlock usage mixes `spin_lock()` in xmit and `spin_lock_bh()` in work/close.

## Test Signals
Serdev probe with `current-speed`, open/close queue state, TX partial-write wakeups, RX frame decode, timeout accounting, random/static MAC assignment, and remove cleanup are the primary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_uart.c -->
