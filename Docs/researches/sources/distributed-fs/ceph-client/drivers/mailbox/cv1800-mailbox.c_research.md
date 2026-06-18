<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/cv1800-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/cv1800-mailbox.c

## Purpose
`cv1800-mailbox.c` implements the Sophgo CV1800B mailbox. It exposes eight fixed channels carrying 8-byte messages through per-channel context memory and interrupt bits.

## Important APIs, Types, and Functions
`struct cv1800_mbox` stores the controller, channel-private array, channel array, pending content pointers, base MMIO address, and receiver ID. `cv1800_mbox_send_data()` writes a message and triggers a remote CPU interrupt. `cv1800_mbox_irq()` is the top-half interrupt handler, and `cv1800_mbox_isr()` is the threaded handler that copies message data to clients. `cv1800_mbox_xlate()` maps two-cell phandles to channel index and target CPU.

## Control Flow
Probe maps registers, configures mailbox core with polling TX completion, requests a threaded IRQ, initializes channel private indexes, stores drvdata, and registers the controller. Sending copies eight bytes to the channel context, clears/sets remote CPU bits, enables the channel bit, and writes the global set register. The hard IRQ reads set-interrupt bits for `RECV_CPU`, records context pointers for active channels, clears the interrupt, disables the channel bit, and wakes the thread. The thread copies each pending 64-bit message and calls `mbox_chan_received_data()`.

## State and Persistence
`content[]` is a transient handoff from top half to thread. Channel private state stores the channel index and target CPU selected by xlate. Hardware enable bits represent TX completion for `last_tx_done()`.

## Dependencies and Integration Points
The driver uses platform MMIO, threaded IRQs, mailbox core, OF compatible `sophgo,cv1800b-mailbox`, and two-cell mailbox specifiers `(channel, cpu)`.

## Risks and Edge Cases
`cv1800_mbox_xlate()` does not validate `args_count` or CPU range. The threaded handler sends a pointer to a stack `u64`; mailbox callbacks must consume it synchronously. Interrupt handling disables each channel by writing `~valid` as a byte, which is hardware-specific and sensitive to bit semantics. Only fixed 8-byte payloads are supported.

## Test Signals
Validate all eight channels, remote CPU phandle values, 8-byte payload integrity, hard/threaded IRQ handoff, TX completion polling, invalid channel rejection, and no lost messages when several channel bits arrive in one interrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/cv1800-mailbox.c -->
