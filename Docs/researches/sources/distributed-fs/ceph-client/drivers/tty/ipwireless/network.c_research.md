# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/network.c

## Purpose
`network.c` bridges IPWireless card channels to Linux `ppp_generic` and associated diagnostic ttys. It registers a PPP channel when the modem tty opens, sends outbound PPP frames to the hardware RAS channel, routes inbound data to PPP or tty devices, propagates modem-control changes, and manages PPP open/close work asynchronously.

## Important APIs, Types, And Functions
- `struct ipw_network` stores hardware, optional `ppp_channel`, associated tty matrix, queue/backpressure counters, locks, PPP ioctl state, RAS control lines, and online/offline work.
- `ipwireless_ppp_start_xmit` prepends the PPP `0xff 0x03` header, enforces `ipwireless_out_queue`, submits to `ipwireless_send_packet`, and blocks PPP output when full.
- `notify_packet_sent` decrements queued packets and wakes PPP output if it was blocked.
- `ipwireless_ppp_ioctl` implements PPP flags, async maps, and MRU ioctls.
- `do_go_online`/`do_go_offline` allocate/register and unregister the `ppp_channel`.
- `ipwireless_network_packet_received` routes online modem RAS data to PPP and other channel data to ttys.
- Lifecycle and association APIs include create/free, PPP open/close, tty association, and PPP metadata queries.

## Control Flow And State
Creation initializes locking and work items, stores the hardware pointer, and associates the network object with hardware. Opening the modem tty schedules PPP registration. Closing schedules PPP unregistration under `close_lock`.

Outbound PPP is accepted only while queued packets are below the module queue limit. The function reserves a queue slot, prepends or copies the PPP header, submits the packet with a completion callback, frees the skb on success, and returns accepted ownership. Full queues set `ppp_blocked` and rely on completion wakeups.

Inbound packets fan out to associated ttys. RAS packets with DCD asserted and a modem tty are converted to skbs, stripped of an optional PPP header, and delivered to `ppp_input`; all other packets are delivered through `ipwireless_tty_received`.

## State And Persistence Behavior
Runtime state includes the PPP channel pointer, queue counters, blocked flag, MRU/ACCM/ioctl state, associated tty pointers, and cached RAS control lines. No durable storage is used. `shutting_down` is set during free but is not otherwise meaningful in this file.

## Dependencies And Integration Points
The file depends on PPP generic APIs, skbuffs, workqueues, spinlocks, mutexes, and local hardware/tty APIs. Hardware integration is through packet send, interrupt stop, and network association. TTY integration is through receive delivery and control-line notifications.

## Risks And Edge Cases
If `ipwireless_send_packet` fails after `outgoing_packets_queued` is incremented, this function does not decrement the counter, so repeated failures can create stale backpressure. Associated tty arrays are not explicitly locked, relying on lifecycle ordering. PPP input drops the spinlock before calling into PPP, so `close_lock` is the key guard against channel teardown.

## Test Signals
Open/close modem tty and verify PPP channel registration. Drive TX until queue blocking and confirm wakeup on completion. Receive RAS packets with and without PPP header. Toggle DCD to verify routing changes. Teardown under traffic to catch workqueue and close races.
