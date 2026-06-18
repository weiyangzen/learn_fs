# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-xgene-slimpro.c

Purpose: drives the AppliedMicro/APM X-Gene SLIMpro mailbox controller, exposing up to eight doorbell channels with independent register windows and IRQs for firmware communication.

Important APIs/types/functions: `struct slimpro_mbox_chan` stores per-channel MMIO, IRQ, channel pointer, and a three-word RX buffer. `struct slimpro_mbox` owns the mailbox controller and channel arrays. The mailbox ops are `slimpro_mbox_send_data`, `slimpro_mbox_startup`, and `slimpro_mbox_shutdown`; helpers read/write doorbell data and status bits.

Control flow: probe maps the controller window, discovers consecutive IRQs, initializes per-channel register offsets spaced by `MBOX_REG_SET_OFFSET`, and registers a txdone-IRQ controller. Startup requests the channel IRQ, clears/enables ACK and available status, and unmasks interrupts. Sending writes data words 1 and 2 before the doorbell word 0. IRQ handling checks ACK status to call `mbox_chan_txdone`, checks available status to copy three RX words, clears status bits, and calls `mbox_chan_received_data`.

State and persistence: only volatile MMIO and per-channel `rx_msg[3]` are maintained. IRQ resources are requested on channel startup and freed on shutdown through devm helpers.

Dependencies and integration: supports OF `apm,xgene-slimpro-mbox` and ACPI `APMC0D01`, uses the mailbox controller framework, and is registered at `subsys_initcall` so firmware clients can bind early.

Risks: channel count is truncated at the first missing IRQ; clients must use exactly the three-word message format. `devm_request_irq` inside startup paired with `devm_free_irq` is unusual but explicit.

Test signals: ACPI and DT probe, all channel IRQ discovery, ACK-only and RX-only interrupt paths, and firmware echo tests that validate word ordering.
