<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox_client.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox_client.h

## Purpose
This is the public client-side interface to the Linux mailbox framework. It lets device drivers request mailbox channels, send messages, receive callbacks, flush blocking transfers, and release channels.

## Important APIs, types, and functions
`struct mbox_client` identifies the client device and TX policy: `tx_block`, `tx_tout`, `knows_txdone`, and optional `rx_callback`, `tx_prepare`, and `tx_done` callbacks. Public APIs include `mbox_bind_client`, `mbox_request_channel_byname`, `mbox_request_channel`, `mbox_send_message`, `mbox_flush`, `mbox_client_txdone`, `mbox_client_peek_data`, `mbox_chan_tx_slots_available`, and `mbox_free_channel`.

## Control flow
A driver fills `struct mbox_client`, requests a channel by name or index, submits messages, and optionally receives RX/TX callbacks in atomic context. If the client knows when TX is done, it calls `mbox_client_txdone()` to advance the framework state. Blocking clients can use `tx_block`/`tx_tout` and `mbox_flush()`.

## State and persistence
Client state is owned by the driver. The framework stores the client pointer in the channel while the channel is bound. There is no persistent storage; channel ownership ends with `mbox_free_channel()`.

## Dependencies and integration points
It depends on Linux device and OF support and is paired with `mailbox_controller.h`. Integration points are firmware/DT channel lookup, controller-specific transport drivers, and subsystem clients such as firmware, remoteproc, RPMI, and vendor IPC.

## Risks and test signals
Callbacks can be atomic, so sleeping operations in `rx_callback`, `tx_prepare`, or `tx_done` are risky. Clients must match TX completion mode with controller capabilities and avoid freeing message memory before completion. Test named/indexed channel lookup, blocking timeout, ACK-driven completion, RX callback delivery, and channel release during idle and queued states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox_client.h -->
