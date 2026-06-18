# sources/distributed-fs/ceph-client/drivers/mailbox/platform_mhu.c

Purpose: implements a simple platform ARM MHU-style mailbox for Amlogic Meson GXBB, exposing three channels for secure, low-priority, and high-priority interrupt lines.

Important APIs/types/functions: `struct platform_mhu` contains the MMIO base, three `platform_mhu_link` records, three channels, and controller. Ops are `platform_mhu_send_data`, startup/shutdown, and `platform_mhu_last_tx_done`; `platform_mhu_rx_interrupt` handles incoming data.

Control flow: probe maps the register resource, assigns each channel an IRQ and RX/TX register pair using fixed offsets, then registers a poll-txdone controller. Startup clears any stale TX status and requests the channel IRQ. TX writes the caller's `u32` to `INTR_SET_OFS` in the TX register bank. RX IRQ reads `INTR_STAT_OFS`, reports the status word via `mbox_chan_received_data`, and clears it. Txdone polls the TX status register until zero.

State and persistence: all channel state is in fixed MMIO status bits and per-channel link descriptors. No payload buffering or persistent data exists.

Dependencies and integration: depends on DT compatible `amlogic,meson-gxbb-mhu`, three IRQ resources, one MMIO resource, and mailbox clients that use 32-bit status words.

Risks: fixed three-channel layout assumes register spacing exactly matches the hardware. RX passes a pointer to a stack-local `u32`; clients must consume synchronously inside the callback, as expected by mailbox semantics.

Test signals: probe with all three IRQs, TX status polling, RX clear behavior, shared client callback correctness, and DT binding resource order tests.
