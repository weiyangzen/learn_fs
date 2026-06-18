<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/armada-37xx-rwtm-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/armada-37xx-rwtm-mailbox.c

## Purpose
`armada-37xx-rwtm-mailbox.c` provides a single-channel mailbox for the Armada 37xx rWTM BIU secure processor interface. It writes command arguments to mailbox parameter registers and reports secure processor return/status words to clients.

## Important APIs, Types, and Functions
`struct a37xx_mbox` stores the device, mailbox controller, MMIO base, and IRQ. `a37xx_mbox_send_data()` accepts `struct armada_37xx_rwtm_tx_msg`, writes 16 argument words and a command word, and checks FIFO readiness/fullness. `a37xx_mbox_receive()` builds `struct armada_37xx_rwtm_rx_msg` from return/status registers. `a37xx_mbox_irq_handler()`, `a37xx_mbox_startup()`, and `a37xx_mbox_shutdown()` manage completion interrupts.

## Control Flow
Probe allocates one channel, maps the register resource, obtains the IRQ, initializes mailbox core state with `txdone_irq = true`, and registers the controller. Startup requests the IRQ and unmasks command-complete and queue-full interrupts. Send checks for null data, warns if the secure processor is not ready, rejects a full FIFO with `-EBUSY`, writes arguments, and posts the command. The IRQ handler reads interrupt status, receives response data on `SP_CMD_COMPLETE`, logs queue-full errors, clears status by writing it back, and reports TX completion.

## State and Persistence
All driver state is devm-managed per platform device. Runtime interrupt mask state is enabled on startup and disabled on shutdown. No command queue is mirrored in software; clients are expected to serialize through the mailbox framework and hardware FIFO status.

## Dependencies and Integration Points
The driver depends on the Linux mailbox core, platform MMIO/IRQ helpers, OF compatible `marvell,armada-3700-rwtm-mailbox`, and the public message structs from `include/linux/armada-37xx-rwtm-mailbox.h`.

## Risks and Edge Cases
The hardware has only one channel and a small FIFO depth, so clients must handle `-EBUSY`. Startup uses devm IRQ request/free on channel open/close, so repeated open/close paths should be tested. Queue-full interrupt bits are logged but do not synthesize a data response. Secure processor "not ready" is only a warning before attempting the command.

## Test Signals
Test signals include command/response round trips with all 16 argument/status words, queue-full handling, IRQ mask toggling on startup/shutdown, no IRQ behavior after shutdown, and DT probe failures for missing MMIO or IRQ resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/armada-37xx-rwtm-mailbox.c -->
