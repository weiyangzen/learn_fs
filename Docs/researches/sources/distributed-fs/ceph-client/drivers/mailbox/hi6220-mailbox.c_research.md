<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/hi6220-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/hi6220-mailbox.c

## Purpose
`hi6220-mailbox.c` implements the HiSilicon Hi6220 mailbox with 32 channels, supporting TX and RX semantics through shared slot data registers and ACK interrupt vectors.

## Important APIs, Types, and Functions
`struct hi6220_mbox` stores IPC registers, mailbox buffer registers, IRQ mapping, controller, channel count, and flexible per-channel state. `struct hi6220_mbox_chan` stores direction, destination IRQ, ack IRQ, slot, and parent. Important functions are `hi6220_mbox_send_data()`, `hi6220_mbox_interrupt()`, `hi6220_mbox_startup()`, `hi6220_mbox_shutdown()`, `hi6220_mbox_last_tx_done()`, and `hi6220_mbox_xlate()`.

## Control Flow
Probe maps IPC and buffer resources, requests the shared IRQ, initializes controller/channels, clears interrupt state, selects IRQ-based or polling TX completion based on `hi6220,mbox-tx-noirq`, registers the controller, and runs at `core_initcall`. Xlate takes `(slot, dst_irq, ack_irq)`, validates all against channel count, prevents duplicate ack IRQ mapping, and returns the slot channel. Startup enables the ack interrupt. Send marks the channel TX, sets slot state to TX, selects ACK IRQ or automatic mode, writes eight words, and triggers the remote destination IRQ. The ISR reads ACK status bits, maps them to channels, completes TX channels or reads eight-word RX data for non-TX channels, clears the ack IRQ, and returns the slot to idle.

## State and Persistence
`irq_map_chan[]` ties ack interrupt vectors to channels until shutdown. Each `mchan` persists current direction and slot configuration. Hardware slot state is actively rewritten to idle after interrupts.

## Dependencies and Integration Points
The driver depends on platform MMIO/IRQ, OF compatible `hisilicon,hi6220-mbox`, optional DT property `hi6220,mbox-tx-noirq`, mailbox core, and early registration.

## Risks and Edge Cases
`last_tx_done()` has a `BUG_ON()` if called in IRQ mode, so mailbox configuration must match the selected completion mode. RX uses stack message storage for synchronous delivery. Direction is set to TX on send and reset to 0 on startup, making mixed client behavior sensitive to open/send ordering. Duplicate ack IRQ detection only rejects the same channel pointer case.

## Test Signals
Validate TX IRQ and polling modes, ACK vector mapping and cleanup, eight-word RX/TX payloads, unexpected IRQ vector warnings, invalid xlate arguments, slot idle completion, and suspend/resume users that depend on early mailbox registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/hi6220-mailbox.c -->
