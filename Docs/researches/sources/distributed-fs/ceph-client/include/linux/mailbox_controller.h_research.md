<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox_controller.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox_controller.h

## Purpose
This header defines the provider/controller side of the Linux mailbox framework: controller registration, channel operations, TX-done detection modes, per-channel queues, and atomic notification entry points.

## Important APIs, types, and functions
`struct mbox_chan_ops` supplies controller callbacks for `send_data`, `flush`, `startup`, `shutdown`, `last_tx_done`, and `peek_data`. `struct mbox_controller` describes the controller device, channel array, TX-done policy, firmware/OF translators, and polling timer state. `struct mbox_chan` holds runtime channel state including owner client, completion, active request, circular queue of `MBOX_TX_QUEUE_LEN` messages, lock, and controller-private data. Public provider APIs are `mbox_controller_register`, `mbox_controller_unregister`, `devm_mbox_controller_register`, `mbox_chan_received_data`, and `mbox_chan_txdone`.

## Control flow
Controller drivers register an initialized `mbox_controller` with channel storage and ops. Client requests call `startup`; sends enqueue or invoke `send_data`; completion is signaled by IRQ, polling via `last_tx_done`, or client ACK via `mbox_client_txdone()`. RX paths call `mbox_chan_received_data()` from atomic context, and channel release calls `shutdown`.

## State and persistence
Runtime state lives in `mbox_controller` and `mbox_chan`: queue indices, message count, active request pointer, locks, completions, and polling timer. There is no on-disk persistence. `MBOX_NO_MSG` distinguishes no active request from a legitimate NULL message.

## Dependencies and integration points
It integrates Linux devices, firmware node and OF lookup, hrtimer polling, completions, spinlocks, and list registration. It is the counterpart to `mailbox_client.h` and is used by SoC mailbox controller drivers.

## Risks and test signals
Risks include sleeping from atomic `send_data`, queue overflow, incorrect TX-done mode combinations, stale callbacks after `shutdown`, translator mismatch, and active request lifetime bugs. Test IRQ, polling, and ACK completion modes; queue saturation; concurrent send/free; RX while shutting down; and firmware channel translation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox_controller.h -->
