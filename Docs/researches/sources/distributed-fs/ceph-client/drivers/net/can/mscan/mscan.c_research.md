# sources/distributed-fs/ceph-client/drivers/net/can/mscan/mscan.c

## Purpose
`mscan.c` is the generic SocketCAN driver logic for Freescale/Motorola MSCAN controllers. It handles mode changes, bit timing, TX buffer management, RX/error NAPI polling, interrupts, open/close, and generic device allocation/registration.

## Important APIs, Types, And Functions
- `mscan_bittiming_const` defines classic CAN timing limits.
- `mscan_set_mode()` transitions between normal, sleep, init, and poweroff-style modes using `CANCTL0/CANCTL1` handshakes.
- `mscan_start()` initializes software TX/RX state, clears MPC5121 bus-off hold, enters normal mode, caches status flags, and enables receive interrupts.
- `mscan_restart()` supports CAN restart, with special MPC5121 bus-off hold behavior.
- `mscan_start_xmit()` selects one of three hardware TX buffers, encodes standard/extended CAN IDs and RTR, writes payload and priority, starts transmission, and saves echo skb.
- `mscan_rx_poll()` drains receive and error events through NAPI.
- `mscan_isr()` handles TX completions and schedules RX/error NAPI.
- `register_mscandev()`, `unregister_mscandev()`, and `alloc_mscandev()` are the API used by platform glue.

## Control Flow
Open enables clocks, calls `open_candev()`, enables NAPI, requests IRQ, sets listen-only mode bit, starts the controller, and starts the netdev queue. Close stops the queue, disables NAPI, masks interrupts, enters init mode, closes the candev, frees IRQ, and disables clocks.

TX disables TX interrupts, chooses a free hardware buffer from `~tx_active & MSCAN_TXE`, manages queue stop/priority ordering when hardware buffer priority could reorder frames, writes ID/data/DLC/priority into the selected buffer, starts transmission with `CANTFLG`, queues echo state in a linked list, marks the buffer active, and reenables TX interrupts for active buffers.

The ISR first handles TX complete flags by walking `tx_head`, reclaiming echo skbs, updating stats, clearing active bits, and waking the queue when allowed. It then examines receive/error flags and, if no RX poll is already running, shadows interrupt enables, disables receive interrupts, and schedules NAPI.

NAPI loops while RX or error flags are present. RX events allocate a classic CAN skb, decode ID/data from the receive buffer, acknowledge `MSCAN_RXF`, and update stats. Error events build CAN error frames, report overflow and state changes, handle bus-off, and acknowledge error flags.

## State And Persistence
`struct mscan_priv` stores controller type, flags, mapped register base, clocks, cached status/interrupt masks, TX priority and active-buffer state, a linked list of TX queue entries, and NAPI. Hardware acceptance filters are initialized to accept all frames. No persistent storage is used.

## Dependencies And Integration Points
The file depends on SocketCAN, NAPI, netdevice, classic CAN skb helpers, Linux IO accessors, clocks, and register definitions from `mscan.h`. It is linked with `mpc5xxx_can.c`, which supplies mapped resources and clock source selection.

## Risks And Edge Cases
- There is a stray `#` character at the end of the "Abort transfers before going to sleep" comment line; if present in the actual compilation unit, it would be a syntax/preprocessor issue worth verifying in the full tree context.
- TX ordering is constrained by hardware buffer priorities; the `cur_pri`/`F_TX_WAIT_ALL` logic is subtle and can stop the queue until all buffers drain.
- Sleep-mode entry may fail under bus activity; the driver proceeds to avoid leaving `SLPRQ` stuck.
- Bus-off recovery differs by MPC5121 versus older controllers, including automatic recovery prevention for non-MPC5121.
- Only classic CAN is supported; no CAN FD paths exist.

## Test Signals
Exercise standard and extended IDs, RTR, all three TX buffers, queue stop/wake under sustained TX, RX overflow, state transitions, bus-off and restart, listen-only, 3-sample bit timing, open/close clock balancing, and NAPI scheduling under mixed TX/RX interrupts.
