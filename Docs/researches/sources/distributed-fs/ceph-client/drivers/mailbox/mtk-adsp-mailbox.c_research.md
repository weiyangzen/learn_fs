# sources/distributed-fs/ceph-client/drivers/mailbox/mtk-adsp-mailbox.c

Purpose: provides a one-channel MediaTek ADSP mailbox controller for MT8186 and MT8195 style register layouts. It sends one 32-bit command bitfield and reports RX events without an in-band payload.

Important APIs/types/functions: `struct mtk_adsp_mbox_priv` stores the mailbox controller, mapped registers, and SoC config. `struct mtk_adsp_mbox_cfg` supplies set/clear register offsets. Ops are `mtk_adsp_mbox_send_data`, startup/shutdown, and `mtk_adsp_mbox_last_tx_done`; IRQ handling is split into a top half that clears output bits and a thread that reports data.

Control flow: probe allocates one channel, maps registers, selects match config, requests a threaded IRQ, and registers a poll-txdone mailbox. Startup and shutdown clear inbound/outbound command registers. TX writes the caller's `u32` to `set_in`; polling reports complete when `set_in` becomes zero. IRQ top half reads `set_out`, writes the same value to `clr_out`, and wakes the thread; the thread calls `mbox_chan_received_data(chan, NULL)`.

State and persistence: state is volatile MMIO only. The controller does not buffer payloads and has no persistent configuration beyond match offsets.

Dependencies and integration: depends on DT compatibles `mediatek,mt8186-adsp-mbox` and `mediatek,mt8195-adsp-mbox`, a single MMIO resource, one IRQ, and the generic mailbox framework.

Risks: xlate ignores mailbox specifier contents and always returns channel zero. TX done relies on remote firmware clearing `set_in`; broken firmware causes mailbox core timeouts.

Test signals: boot/probe on both register layouts, command clear on startup/shutdown, RX interrupt clear behavior, and timeout behavior when remote does not clear `set_in`.
