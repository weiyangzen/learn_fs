## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ring2.c

Purpose: implements X-Gene2-specific ring programming and command semantics for the original driver.

Important APIs, types, and functions: ring setup initializes interrupt line and dequeue interrupt bits for CPU-owned rings, writes coherent queue base and message addressing fields, sets ring type/buffer pool mode, recombination timeout, ring IDs, interrupt mailbox DMA address, descriptor empty markers, command counts with interrupt-clear bits, queue length reads, and PBM coalescing registers. It exports `xgene_ring2_ops` with six ring config registers, ring ID shift 13, setup/clear/command/length/coalescing callbacks.

Control flow, state, and persistence: `xgene_enet_setup_ops` selects `xgene_ring2_ops` for `XGENE_ENET2`. Ring creation allocates an interrupt mailbox for CPU-owned rings when required, and setup writes the mailbox base to `CSR_VMID0_INTR_MBOX`.

Dependencies and integration points: depends on shared ring helpers/constants from `xgene_enet_hw.h`, X-Gene2 constants from `xgene_enet_ring2.h`, and private data MMIO bases from `xgene_enet_main.h`.

Risks: X-Gene2 skips ring ID writes for CPU-owned rings but configures interrupt mailboxes; applying X-Gene1 logic would break interrupts. Command writes combine count and interrupt clear, so signed count handling must remain correct for dequeue notifications.

Test signals: X-Gene2 probe, CPU-owned ring interrupts, TX/RX completion, queue length reads, interrupt coalescing behavior, and ring clear on remove.
