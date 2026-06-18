<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-altera.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-altera.c

## Purpose
`mailbox-altera.c` implements the Altera mailbox IP as a one-channel mailbox that can be detected as either sender or receiver. It supports interrupt or polling operation depending on IRQ availability and direction.

## Important APIs, Types, and Functions
`struct altera_mbox` stores direction, interrupt mode, IRQ, MMIO base, controller, optional RX polling timer, and active channel. Helpers include `altera_mbox_is_sender()`, `altera_mbox_full()`, `altera_mbox_pending()`, RX/TX interrupt mask helpers, `altera_mbox_rx_data()`, `altera_mbox_send_data()`, `altera_mbox_startup()`, `altera_mbox_shutdown()`, `last_tx_done()`, and `peek_data()`.

## Control Flow
Probe maps registers, determines sender mode by writing a magic value to the pointer register and reading it back, optionally obtains an IRQ, configures one channel, enables TX IRQ or TX polling for sender instances, and registers the controller. Sender startup requests a TX-space interrupt if in interrupt mode. Receiver startup requests an RX-pending interrupt or falls back to a 5 ms polling timer. Send validates direction and non-null data, rejects a full mailbox, enables TX interrupt before sending if needed, writes pointer first and command second. RX reads pointer and command when pending and reports a two-word array.

## State and Persistence
Direction is determined once at probe. `intr_mode` may be downgraded to polling if RX IRQ request fails. The RX polling timer persists only while a receiver channel is active. There is no message queue outside the hardware registers.

## Dependencies and Integration Points
The driver depends on platform MMIO/IRQ, OF compatible `altr,mailbox-1.0`, Linux timers, and mailbox core operations including `peek_data()`.

## Risks and Edge Cases
Direction detection mutates the pointer register with a magic value. Receiver polling uses a timer and stack-local data for synchronous delivery. Shutdown masks all interrupts and frees the IRQ in interrupt mode. Send must preserve pointer-before-command ordering because command write likely triggers delivery.

## Test Signals
Test sender and receiver hardware variants, IRQ and polling receiver paths, failed IRQ fallback, pointer/command ordering, full and pending status handling, timer cancellation on shutdown, and `peek_data()` correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-altera.c -->
