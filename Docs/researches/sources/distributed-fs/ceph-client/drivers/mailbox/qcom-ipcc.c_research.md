# sources/distributed-fs/ceph-client/drivers/mailbox/qcom-ipcc.c

Purpose: implements Qualcomm IPCC as both an IRQ controller for received client/signal pairs and an optional mailbox controller for sending IPCC signals described by DT `mboxes` properties.

Important APIs/types/functions: `struct qcom_ipcc` owns MMIO base, IRQ domain, dynamically sized mailbox channels, per-channel client/signal info, and summary IRQ. `qcom_ipcc_get_hwirq` encodes client/signal into a hardware IRQ. Key functions include IRQ domain map/xlate, mask/unmask, summary IRQ dispatch, mailbox send/xlate/shutdown, mbox setup, PM resume, probe/remove.

Control flow: probe maps registers, disables firmware-set clear-on-read mode if present, creates an IRQ domain, scans all available DT nodes with `mboxes` references to count channels targeting this controller, registers a mailbox controller if needed, and requests the summary IRQ. Summary IRQ repeatedly reads `RECV_ID` until no pending IRQ, clears each signal, finds the Linux virq, and calls `generic_handle_irq`. Mailbox xlate allocates a free channel for a unique client/signal pair; send writes the encoded pair to `SEND_ID`.

State and persistence: IRQ domain mappings persist while bound. Mailbox channel `con_priv` is allocated per requested client/signal and cleared on shutdown. Hardware receive enable/disable state is managed by IRQ chip callbacks.

Dependencies and integration: depends on DT interrupt-controller and mailbox bindings, generic IRQ domain APIs, mailbox framework, and early `arch_initcall` registration.

Risks: `generic_handle_irq` is called even if mapping lookup returns zero; valid DT interrupt mappings are required. Mailbox channels are sized by scanning existing DT clients, so late/unusual clients cannot exceed that count.

Test signals: IRQ domain xlate for three-cell specs, mailbox duplicate-pair rejection, summary IRQ dispatch/clear loop, suspend resume pending logging, and no-client mailbox skip path.
