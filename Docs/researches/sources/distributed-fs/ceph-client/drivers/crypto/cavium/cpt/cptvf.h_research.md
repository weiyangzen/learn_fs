# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf.h

Purpose: declares VF-side Thunder CPT state, command/pending queue layouts, interrupt constants, DMA modes, mailbox function prototypes, and crypto/request integration hooks.

Important APIs and types: constants define default command queue length/chunking, timeout, MSI-X vector count, interrupt masks, and DMA modes. `struct command_chunk`, `command_queue`, and `command_qinfo` describe circular coherent instruction chunks. `struct pending_entry`, `pending_queue`, and `pending_qinfo` track submitted requests and completions. `struct cpt_vf` stores PCI/BAR state, VF identity/type/group, queue resources, IRQ affinity masks, and mailbox ACK flags.

Control flow and state: the VF driver allocates command queues, pending queues, tasklets, and MSI-X vectors, then transitions to device-ready after PF mailbox negotiation and VQ programming. Pending entries persist until request completion or timeout cleanup.

Dependencies and integration points: shared by VF main, mailbox, request manager, and crypto algorithm files. It depends on `cpt_common.h`, Linux lists, PCI, DMA, and tasklet/IRQ code.

Risks and test signals: risks include fixed one-queue-per-VF assumptions, typo-prone mailbox ACK booleans without locking, pending queue wrap-around bugs, and cleanup needing to quiesce tasklets before queue memory free. Test signals include VF probe, two MSI-X handlers registered, PF negotiation setting `vfid` and `vftype`, queue doorbells incrementing, and request completions draining pending entries.
