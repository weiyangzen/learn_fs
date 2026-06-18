<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/hi3660-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/hi3660-mailbox.c

## Purpose
`hi3660-mailbox.c` implements the HiSilicon Hi3660 mailbox controller with up to 32 channels. It is primarily a TX-oriented mailbox that writes eight-word messages and triggers a destination interrupt vector.

## Important APIs, Types, and Functions
`struct hi3660_mbox` owns the register base, channel array, per-channel IRQ vectors, and controller. `struct hi3660_chan_info` stores destination and acknowledge IRQ bits. Key routines are `hi3660_mbox_unlock()`, `hi3660_mbox_acquire_channel()`, `hi3660_mbox_check_state()`, `hi3660_mbox_startup()`, `hi3660_mbox_send_data()`, and `hi3660_mbox_xlate()`.

## Control Flow
Probe maps the MMIO region, configures 32 channels with their index stored in `con_priv`, sets mailbox ops/xlate, registers the controller, and runs at `core_initcall`. Xlate takes three cells `(channel, dst_irq, ack_irq)` and stores vectors in `mchan`. Startup unlocks IPC registers and acquires the channel by waiting for idle state and setting the ack IRQ in `SRC`. Send waits for ready or an ACK state, clears the destination interrupt mask, writes destination and automatic-ack mode, fills eight data registers, and writes `SEND` with the ack IRQ bit.

## State and Persistence
Per-channel destination/ack vector selections persist in `mchan[]` after xlate. The hardware channel state machine is polled on each send. There is no explicit shutdown operation and no software queue.

## Dependencies and Integration Points
The driver integrates with the mailbox core, platform MMIO, OF compatible `hisilicon,hi3660-mbox`, delay/poll helpers, and early platform driver registration.

## Risks and Edge Cases
`hi3660_mbox_xlate()` validates only the channel index, not dst/ack IRQ ranges. Channel acquisition uses a short retry loop without delay. Send assumes the payload contains eight `u32` words. ACK polling can block up to 300 ms and returns timeout errors on stuck hardware.

## Test Signals
Test unlock and acquire success/failure, all 32 channel xlate values, eight-word data transfer, ACK timeout handling, invalid channel rejection, and early boot client availability due to `core_initcall`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/hi3660-mailbox.c -->
