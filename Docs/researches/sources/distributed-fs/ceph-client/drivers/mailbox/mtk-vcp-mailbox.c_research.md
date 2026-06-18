# sources/distributed-fs/ceph-client/drivers/mailbox/mtk-vcp-mailbox.c

Purpose: provides a single-channel MediaTek VCP mailbox controller for MT8196, transferring IPI messages through a fixed-size shared slot window and bit-indexed interrupt registers.

Important APIs/types/functions: `struct mtk_vcp_mbox` holds the controller, one channel, mapped base, config offsets, and an `mtk_ipi_info` receive buffer. `struct mtk_vcp_mbox_cfg` supplies `set_in` and `clr_out`. Ops are `mtk_vcp_mbox_send_data` and `mtk_vcp_mbox_last_tx_done`, with `mtk_vcp_mbox_xlate` enforcing zero cells.

Control flow: probe allocates one channel, an RX message buffer of `MTK_VCP_MBOX_SLOT_MAX_SIZE`, maps registers, gets match data, requests a threaded IRQ, and registers a poll-txdone controller. TX validates `mtk_ipi_info->msg`, checks whether the `set_in` bit for the IPI index is busy, bounds-checks slot offset plus length, copies the payload to IO memory, and sets the bit. The IRQ thread reads `clr_out` status, copies the full slot window into `ipi_recv.msg`, passes `ipi_recv` to the client, and clears the status bits. Txdone polls until the active request's bit in `set_in` clears.

State and persistence: runtime state is the receive scratch `ipi_recv` and active mailbox request pointer held by the core. Hardware slot contents are transient.

Dependencies and integration: depends on `linux/mailbox/mtk-vcp-mailbox.h`, one IRQ, one MMIO window, DT `mediatek,mt8196-vcp-mbox`, and clients that understand `mtk_ipi_info`.

Risks: `last_tx_done` dereferences `chan->active_req` as `mtk_ipi_info`; malformed clients can crash or mispoll. IRQ copies the full slot window regardless of reported status.

Test signals: busy-bit rejection, slot bounds validation, RX status clearing, txdone polling by IPI index, and zero-cell DT xlate checks.
