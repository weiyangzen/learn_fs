# sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhu.c

## Purpose
Implements the original ARM Message Handling Unit mailbox controller driver for AMBA devices with three physical channels: low priority, high priority, and secure.

## Important APIs, Types, And Functions
`struct mhu_link` stores one channel's IRQ and TX/RX register bases. `struct arm_mhu` stores the mapped base, three links, three mailbox channels, and the controller. Mailbox ops are `mhu_send_data()`, `mhu_startup()`, `mhu_shutdown()`, and `mhu_last_tx_done()`. `mhu_rx_interrupt()` reads interrupt status, reports the 32-bit value to the mailbox client, and clears the same bits.

## Control Flow
Probe requires OF compatible `"arm,mhu"`, maps the AMBA resource, assigns each channel an IRQ and register window, configures mailbox polling for TX completion, and registers the controller. Startup clears any pending TX status and requests the channel IRQ. Sending writes the caller-provided `u32` to `INTR_SET`; TX is complete when the peer clears `INTR_STAT`.

## State, Dependencies, And Integration
State is per AMBA device and per channel. The driver depends on AMBA probing, MMIO accessors, interrupts, OF compatible matching, and the generic mailbox controller framework. Clients reference channels from device tree using the standard mailbox binding for this controller.

## Risks And Test Signals
It trusts `data` to point to a `u32`. IRQs are requested per channel on startup with `IRQF_SHARED`, so teardown and duplicate startup paths matter. Secure channel availability is hardware/security-state dependent but still exposed as one of three channels. Test signals include RX interrupt clear behavior, TX polling, absent/invalid IRQs, shared IRQ handling returning `IRQ_NONE` when status is zero, and channel ordering in device-tree clients.
