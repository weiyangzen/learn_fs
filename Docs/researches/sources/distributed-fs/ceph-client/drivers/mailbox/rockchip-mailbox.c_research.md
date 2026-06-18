# sources/distributed-fs/ceph-client/drivers/mailbox/rockchip-mailbox.c

Purpose: implements the Rockchip RK3368 mailbox used for CPU-to-MCU communication, exposing four channels with command/data register pairs and per-channel B2A IRQs.

Important APIs/types/functions: `struct rockchip_mbox_msg` contains command and expected RX size. `struct rockchip_mbox_chan` tracks channel index, IRQ, in-flight message pointer, and parent. `struct rockchip_mbox` owns controller, clock, MMIO base, buffer size, and flexible channel array. Ops are send, startup, and shutdown; IRQ handling is split top/thread.

Control flow: probe allocates controller and channel arrays, maps MMIO, computes per-direction buffer size from resource size, enables `pclk_mailbox`, requests a threaded IRQ per channel, and registers a txdone-IRQ controller. Startup enables all B2A interrupts. Send validates the message and RX size, stores the message pointer in the channel state, writes command and RX size to A2B registers, and returns. Top-half IRQ checks B2A status for the matching channel, clears the bit, and wakes the thread. The threaded handler retrieves the stored message, calls `mbox_chan_received_data` with it, and clears the in-flight pointer.

State and persistence: the current message pointer is stored per channel until the B2A interrupt arrives. Clock enable persists while the device is bound; there is no remove clock-disable path in this file.

Dependencies and integration: depends on DT `rockchip,rk3368-mailbox`, one clock, per-channel IRQ resources, and mailbox clients using `rockchip_mbox_msg`.

Risks: send uses `struct rockchip_mbox_chan *chans = mb->chans` and then `chans->idx`, effectively channel zero, instead of deriving the channel from `chan`; this is a likely multi-channel bug. No txdone callback is issued despite `txdone_irq = true`.

Test signals: multi-channel send/interrupt tests, clock lifecycle checks, RX size validation, and mailbox-core timeout behavior for clients expecting txdone.
