# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/mailbox.c

Purpose: This file implements the SCMI mailbox transport using Linux mailbox channels and shared memory. It supports one bidirectional channel, separate A2P/P2A channels, and optional completion channels depending on device-tree `mboxes`/`shmem` layout.

Important APIs/types/functions: `struct scmi_mailbox` stores mailbox client/channels, SCMI channel info, shmem mapping, channel mutex, and IO ops. `mailbox_chan_validate()` validates and maps mailbox indices. `mailbox_chan_setup()` maps shmem, requests mailbox channels, and initializes state. `mailbox_send_message()` serializes sends through `chan_lock`. `mailbox_mark_txdone()` calls mailbox txdone and unlocks. Fetch/clear/poll helpers delegate to shared memory ops. `scmi_mailbox_desc` advertises timeout, max messages, and max payload.

Control flow: The mailbox core calls `tx_prepare()` before sending to write the SCMI shared memory message. RX callbacks reject spurious A2P IRQs when the channel is not free and otherwise call the SCMI core RX callback with the shared-memory header. Send locks the channel, submits the xfer to the mailbox layer, and leaves the lock held until the SCMI core calls mark_txdone after response processing. Clearing a P2A channel can send an interrupt/doorbell back to firmware if the shmem flags request it.

State and persistence: Per-channel transport state is devm-managed and attached to `cinfo->transport_info`. The mailbox lock prevents mailbox queueing from invalidating SCMI timeouts. There is no persistent storage.

Dependencies and integration points: It depends on the Linux mailbox framework, device tree, shared memory operations, and the SCMI transport driver macro. It matches `arm,scmi`.

Risks and edge cases: Device-tree validation is strict about allowed mailbox/shmem counts but supports several layouts, so binding tests are important. Spurious IRQ detection matters after timeouts. If `mbox_send_message()` fails, the mutex is unlocked immediately; otherwise completion must always reach `mark_txdone()` to avoid deadlock. The descriptor `max_msg` is limited by mailbox queue length.

Test signals: Validate DT layouts with 1 to 4 mailboxes and 1 to 2 shmem entries, TX/RX-only setup, spurious late IRQ tracing, polling completion, P2A notification clear doorbell, mailbox send failure, and timeout behavior with serialized channel locking.
