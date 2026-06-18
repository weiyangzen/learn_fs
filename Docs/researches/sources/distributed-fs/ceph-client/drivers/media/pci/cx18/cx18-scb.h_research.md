# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-scb.h

Defines the CX23418 SCB hardware ABI: interrupt bit constants, `SCB_OFFSET`, `SCB_RESERVED_SIZE`, `struct cx18_mdl_ent`, and the large `struct cx18_scb` containing processor states, mailbox offsets, mailboxes, MDL acknowledgements, and flexible-array MDL descriptors.

The stream queue layer writes `cpu_mdl[]`; stream startup passes firmware offsets to `cpu_mdl_ack`; mailbox code depends on offsets initialized by `cx18_init_scb`. This makes the file central to firmware IPC and DMA exchange.

State described by this header lives in firmware-visible encoder memory. Risks are layout or numeric changes, SCB overflow from too many buffers, and mismatched firmware assumptions. Test signals include mailbox ping, DMA done notifications, stream startup, and high-buffer-count failure handling.
