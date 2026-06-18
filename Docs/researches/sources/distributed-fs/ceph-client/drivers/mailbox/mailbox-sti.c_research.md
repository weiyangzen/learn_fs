# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-sti.c

Purpose: implements the STMicroelectronics STi mailbox controller, exposing up to 20 dynamic mailbox channels backed by STi hardware instances and per-instance channel bits. It supports TX-only operation when no IRQ is present and TX/RX operation when an IRQ is supplied.

Important APIs/types/functions: `struct sti_mbox_device`, `struct sti_mbox_pdata`, and `struct sti_channel` hold controller, SoC limits, and allocated channel identity. The mailbox ops are `sti_mbox_startup_chan`, `sti_mbox_shutdown_chan`, `sti_mbox_send_data`, and `sti_mbox_tx_is_ready`; `sti_mbox_xlate` maps two-cell DT specifiers to an available `mbox_chan`.

Control flow: probe reads match data, maps registers, allocates channel slots, registers a polling-txdone controller, and optionally installs a threaded IRQ. Startup clears/enables a requested hardware channel. TX writes the channel bit to `STI_IRQ_SET_OFFSET`. The hard IRQ validates enabled channels, disables the interrupt source, and wakes the thread; the thread drains pending instance bits, reports `mbox_chan_received_data(chan, NULL)`, clears the IRQ, and reenables the channel.

State and persistence: state is volatile MMIO plus `enabled[]`, protected by `mdev->lock`, and per-channel `con_priv` allocated during xlate then cleared on shutdown. No data payload is stored by the driver; it signals events only.

Dependencies and integration: depends on DT compatible `st,stih407-mailbox`, `mbox-name`, the generic mailbox framework, platform IRQ/MMIO resources, and `devm_mbox_controller_register`.

Risks: channel allocation is dynamic and must avoid stale `con_priv`; IRQ handling assumes enable state mirrors hardware. TX completion is inferred by polling enable/status bits, so missed clears can stall the mailbox queue.

Test signals: boot/probe with and without IRQ, DT two-cell xlate bounds tests, RX interrupt storm/spurious IRQ tests, and mailbox client TX timeout coverage.
