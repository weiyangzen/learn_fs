# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_x25.c

## Purpose
`hdlc_x25.c` bridges generic HDLC devices to the kernel LAPB/X.25 stack. It accepts X.25 pseudo-header commands from upper layers, passes data through LAPB, and sends LAPB connect/disconnect/data indications back through the X.25 network stack.

## Important APIs, Types, And Functions
`struct x25_state` contains `x25_hdlc_proto` settings, an `up` flag with spinlock, a receive queue, and a tasklet. Important callbacks are `x25_open()`, `x25_close()`, `x25_rx()`, `x25_xmit()`, `x25_data_indication()`, `x25_data_transmit()`, and the connect/disconnect helpers. The protocol object supplies `.open`, `.close`, `.ioctl`, `.netif_rx`, and `.xmit`.

## Control Flow
Protocol selection validates optional X.25 settings or applies backward-compatible defaults, attaches hardware as NRZ/CRC16, allocates `x25_state`, initializes queues and tasklet, sets `ARPHRD_X25`, and adjusts headroom for the one-byte pseudo-header versus LAPB header insertion. Device open registers LAPB callbacks, applies DCE/modulo/window/timer parameters, and marks the state up. Upper-layer transmit first checks the one-byte pseudo-header: data is sent by `lapb_data_request()`, connect by `lapb_connect_request()`, and disconnect by `lapb_disconnect_request()`. Received HDLC frames are passed into `lapb_data_received()` while up. LAPB callbacks enqueue X.25 pseudo-header indications and schedule the tasklet to call `netif_receive_skb_core()`.

## State And Persistence
All state is per-device volatile memory. The `up` flag serializes data paths against close. `rx_queue` buffers indications until tasklet processing. `x25_close()` marks the link down, unregisters LAPB, and kills the tasklet.

## Dependencies And Integration Points
The module depends on generic HDLC, the kernel LAPB implementation, `<net/x25device.h>` helpers such as `x25_type_trans()`, tasklets, skb queues, and WAN ioctls.

## Risks
`x25_open()` returns errors after `lapb_register()` if `lapb_getparms()` or `lapb_setparms()` fails without explicitly unregistering LAPB in those intermediate paths. Data transmit ignores the hardware `xmit()` return value by design. Correct operation requires upper layers to provide the pseudo-header byte. Tasklet and up-lock sequencing are important for preventing delivery after close.

## Test Signals
Test invalid and default settings, LAPB registration failure paths, open/close with queued indications, connect/disconnect pseudo-header handling, data transfer through LAPB, malformed short transmit packets, carrier and dormant state, and tasklet cleanup on close/detach.
