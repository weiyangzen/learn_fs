# sources/distributed-fs/ceph-client/drivers/mailbox/mtk-gpueb-mailbox.c

Purpose: implements the MediaTek GPUEB mailbox for MT8196-class systems, exposing named GPU embedded-controller channels with fixed TX/RX offsets and lengths.

Important APIs/types/functions: `struct mtk_gpueb_mbox`, `struct mtk_gpueb_mbox_chan`, `struct mtk_gpueb_mbox_chan_desc`, and `struct mtk_gpueb_mbox_variant` describe controller resources and channel layouts. Ops are send, startup, shutdown, and `last_tx_done`; IRQ handling uses a shared top half and threaded handler per channel.

Control flow: probe gets the prepared clock, maps data and control register windows, validates per-channel RX sizes, allocates channels, marks each blocked, and registers a poll-txdone controller. Startup clears RX status, enables the clock, clears pending IRQ for the channel, and requests a shared threaded IRQ. The top half checks RX status and atomically transitions the channel to full/blocked before waking the thread. The thread reads the fixed RX buffer into a stack buffer, clears the channel IRQ, calls `mbox_chan_received_data`, and releases the RX status. TX rejects sends while RX status is nonzero, writes 32-bit words to the channel TX window, and sets the IRQ bit. Txdone polls the TX status bit.

State and persistence: per-channel `rx_status` encodes blocked and full states; channel descriptors are static match data. No persistent storage exists.

Dependencies and integration: depends on MT8196 DT match data, two MMIO resources, a shared IRQ, one clock, and mailbox clients using the fixed channel payload sizes.

Risks: TX and RX share an atomic status gate, so long client callbacks can make TX return `-EBUSY`. The driver intentionally avoids bulk IO helpers for TX ordering; changing that can break hardware expectations.

Test signals: per-channel IRQ routing, RX-size validation, TX busy behavior, clock enable/disable on startup/shutdown, and txdone polling against `GPUEB_MBOX_CTL_TX_STS`.
