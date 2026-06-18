# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox.c

Purpose: implements the Linux generic mailbox framework used by controller drivers and mailbox clients. It manages controller registration, channel lookup from firmware descriptions, exclusive client binding, TX queueing, TX completion methods, RX delivery, and managed registration.

Important APIs/types/functions: exported APIs include `mbox_send_message`, `mbox_flush`, `mbox_request_channel`, `mbox_request_channel_byname`, `mbox_bind_client`, `mbox_free_channel`, `mbox_chan_received_data`, `mbox_chan_txdone`, `mbox_client_txdone`, `mbox_client_peek_data`, `mbox_chan_tx_slots_available`, `mbox_controller_register`, `mbox_controller_unregister`, and `devm_mbox_controller_register`. Internal helpers include `add_to_rbuf`, `msg_submit`, `tx_tick`, and the polling hrtimer.

Control flow: clients request channels via fwnode/OF `mboxes` references or bind an existing channel. Binding initializes the ring buffer, active request, completion, and possibly startup. Sending enqueues a message, submits it if no active request exists, and optionally blocks until txdone or timeout. Txdone can be reported by controller IRQ, controller polling through `last_tx_done`, or client ACK. `tx_tick` clears the active request, submits the next queued item, calls client `tx_done`, and completes blocking senders.

State and persistence: global controller list `mbox_cons` is protected by `con_mutex`. Per-channel state includes `cl`, `active_req`, ring-buffer indices/count, `txdone_method`, completion, and spinlock. No state persists beyond runtime binding.

Dependencies and integration: used by all mailbox controllers and clients, integrates with OF/fwnode reference parsing, module reference counting, hrtimers, completions, and devres cleanup.

Risks: callbacks can run in atomic context, so clients and controllers must obey locking constraints. Timeout path calls `tx_tick` and can race with late hardware completion if a controller reports txdone poorly. Message pointers must remain valid until txdone.

Test signals: queue-depth and timeout tests, polling/IRQ/ACK txdone modes, request-by-name parsing, devm unregister cleanup, and races around free while IRQ arrives.
