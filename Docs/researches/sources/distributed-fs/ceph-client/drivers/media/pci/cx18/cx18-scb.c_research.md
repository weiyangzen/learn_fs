# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-scb.c

Initializes the CX23418 System Control Block in encoder memory through `cx18_init_scb`. The SCB is the firmware-visible IPC area containing processor state, interrupt values, mailbox offsets, MDL acknowledgements, and MDL descriptor arrays.

Control flow selects the SCB memory page at `SCB_OFFSET`, zeroes the 64 KiB reserved area, writes all non-ACK and ACK IRQ bit values for CPU/APU/HPU/PPU/EPU communication pairs, writes offsets for every mailbox pair, writes `ipc_offset`, and marks EPU state ready.

Dependencies are cx18 IO helpers and the SCB layout from `cx18-scb.h`. State is MMIO/encoder memory rather than disk persistence. Risks are offset/bit mistakes breaking firmware IPC or DMA completion. Test signals are firmware boot, mailbox command success, interrupt acknowledgement behavior, and capture start after reset.
