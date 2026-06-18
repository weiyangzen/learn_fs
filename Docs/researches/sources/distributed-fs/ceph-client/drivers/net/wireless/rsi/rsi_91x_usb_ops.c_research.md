# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_usb_ops.c

## Purpose
This file provides the USB RX worker thread that drains SKBs queued by USB URB completion and feeds them into the shared RSI packet parser.

## Important APIs, Types, and Functions
The only function is `rsi_usb_rx_thread(struct rsi_common *common)`.

## Control Flow
The thread waits forever on `dev->rx_thread.event`, resets the event, and drains `dev->rx_q` until empty or shutdown. Each SKB is passed to `rsi_read_pkt(common, skb->data, 0)`, where zero length indicates USB framing rather than a pre-known aggregate byte count. On parser failure it logs and stops the inner drain loop; on shutdown it purges the RX queue and completes the thread completion.

## State and Persistence Behavior
It consumes and purges `struct rsi_91x_usbdev::rx_q`, observes `rx_thread.thread_done`, and completes `rx_thread.completion`. It does not persist hardware state. SKBs remain queued only until the thread drains them or the device is deinitialized.

## Dependencies and Integration Points
It depends on USB private state from `rsi_usb.h`, event helpers in `rsi_common.h`, and the common demultiplexer `rsi_read_pkt`. It is created in `rsi_usb_init_rx` and stopped from USB deinit.

## Risks
If `rsi_read_pkt` returns an error, the current implementation breaks before freeing that SKB, which can leak the failed packet. The thread assumes URB completion only enqueues valid SKBs and that `rsi_kill_thread` wakes the event before waiting. Since USB passes `rcv_pkt_len == 0`, descriptor offset validation in `rsi_read_pkt` is the primary guard against malformed packets.

## Test Signals
Queue drain under sustained URB completions, parser failure handling, thread shutdown with queued packets, RX queue purge on disconnect, and invalid USB aggregate descriptors are the key signals.
