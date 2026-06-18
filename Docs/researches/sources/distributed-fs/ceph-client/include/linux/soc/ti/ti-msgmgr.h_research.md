# sources/distributed-fs/ceph-client/include/linux/soc/ti/ti-msgmgr.h

Purpose: This TI header defines mailbox message manager packet metadata used by TI K3 system firmware communication.

Important APIs/types/functions: It forward-declares `struct mbox_chan` and defines `struct ti_msgmgr_message` with payload length, payload buffer pointer, expected RX channel, and polling timeout in milliseconds.

Control flow: Client drivers fill `ti_msgmgr_message`, pass it to `mbox_send_message`, and optionally use `chan_rx` plus `timeout_rx_ms` when polling for a response.

State and persistence: The struct is transient per mailbox transfer. Hardware mailbox queues and firmware state persist outside the header.

Dependencies and integration: Integrates with the Linux mailbox framework, TI message manager controller, TI SCI firmware, and platform resource-management clients.

Risks and test signals: `len` must match SoC-specific slot sizes, and `chan_rx` must match the expected response path. Test mailbox send/receive, polled timeouts, concurrent clients, and firmware error replies.
