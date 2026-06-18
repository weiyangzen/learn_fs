# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-th1520.c

Purpose: implements the T-Head TH1520 mailbox IPC block for communication from the kernel CPU to three remote ICU CPU targets. It transfers seven 32-bit data words plus a dedicated ACK word and supports IRQ-based txdone.

Important APIs/types/functions: `struct th1520_mbox_priv` owns mapped local/remote ICU windows, clocks, shared IRQ, mailbox controller, and optional suspend context. `struct th1520_mbox_con_priv` binds each channel to local/remote bases and CPU id. Core functions include channel read/write helpers, `th1520_mbox_isr`, `th1520_mbox_send_data`, startup/shutdown, `th1520_mbox_xlate`, and PM callbacks.

Control flow: probe enables four clocks, maps one local and three remote ICU resources, derives per-CPU local windows, initializes four channels, clears/masks hardware, and registers a txdone-IRQ mailbox. Xlate rejects CPU0 because it is the local CPU. Startup clears local/remote data and GEN registers, unmasks the channel bit, and requests the shared IRQ. Send writes INFO0-INFO6 to the remote window and sets the RX-data generate bit. ISR checks the local status map bit, clears it, dispatches incoming data if INFO0 is nonzero, writes the ACK magic to the remote INFO7, optionally generates an ACK interrupt, and calls `mbox_chan_txdone` when local INFO7 contains the magic.

State and persistence: volatile channel registers hold data and ACK state. The driver stores interrupt masks across system sleep; payload registers are explicitly treated as lost during suspend.

Dependencies and integration: depends on named MMIO resources, four named clocks, one shared IRQ, DT `thead,th1520-mbox`, and generic mailbox IRQ txdone semantics.

Risks: the 28-byte payload contract is implicit in callers; CPU1/CPU2 ACK polling differs from CPU3 interrupt behavior. Shared IRQ and per-channel request/free require correct startup/shutdown ordering.

Test signals: multi-channel concurrent client tests, suspend/resume mask restore, busy/ACK timeout tests, and DT resource offset validation, especially the remote-icu0 quirk.
