# sources/distributed-fs/ceph-client/drivers/ata/sata_inic162x.c

## Purpose
`sata_inic162x.c` drives Initio 162x SATA controllers using their IDMA packet engine. The file explicitly warns that the driver has common data-corruption issues and should not be used in production; nevertheless it implements two-port SATA, DMA-assisted PIO/ATAPI handling, custom hardreset, and error recovery.

## Important APIs, Types, and Functions
Important packet types are `struct inic_cpb`, `struct inic_prd`, `struct inic_pkt`, `struct inic_host_priv`, and `struct inic_port_priv`. Core functions include `inic_port_base()`, `inic_reset_port()`, `inic_scr_read/write()`, `inic_stop_idma()`, `inic_host_err_intr()`, `inic_host_intr()`, `inic_interrupt()`, `inic_check_atapi_dma()`, `inic_fill_sg()`, `inic_qc_prep()`, `inic_qc_issue()`, `inic_tf_read()`, `inic_qc_fill_rtf()`, `inic_freeze/thaw()`, `inic_hardreset()`, `inic_error_handler()`, `init_port()`, `inic_port_start()`, `init_controller()`, resume support, and `inic_init_one()`.

## Control Flow, State, and Persistence
Probe prints a corruption warning, allocates a two-port host and private state, enables PCI, selects PCI BAR 5 or CardBus BAR 1, maps MMIO, caches `HOST_CTL`, describes port windows, sets a 32-bit DMA mask, resets the controller, unmasks global port IRQs, sets bus master, and activates libata. Port start allocates coherent `inic_pkt` and CPB lookup table memory, stores addresses in controller registers, and keeps them in `ap->private_data`. `qc_prep` clears and fills the CPB, copies taskfile/LBA48 fields, builds an ATAPI CDB PRD when needed, fills data PRDs, and points CPB table entry 0 at the packet. `qc_issue` starts IDMA by writing host and port control registers and queuing the CPB FIFO. Interrupts dispatch by port, clear IRQ status, inspect IDMA status and CPB response flags, complete successful commands, or freeze/abort on hotplug, PCI, CPB, ATA, spurious, or data over/underflow errors.

## Dependencies and Integration Points
The driver depends on PCI managed MMIO mapping, coherent DMA allocations, libata SATA port ops, SCSI host limits, custom SCR mapping, hardreset via controller IDMA reset rather than standard SControl/SRST signatures, and generic PCI suspend/resume helpers. It constrains DMA boundary and maximum segment size to avoid known hard lockups.

## Risks and Test Signals
Risks are unusually high: documented data corruption, bogus result taskfile sector data, IDMA lockups on 64 KiB PRDs, ATAPI DMA limitations, fragile CPB response interpretation, and controller-specific reset requirements. Tests should be limited to non-production media and include read/write verify under SG boundary stress, LBA48, ATAPI read versus write filtering, hotplug/offline/online interrupts, CPB error injection, hardreset classification, suspend/resume controller reinit, CardBus versus PCI BAR selection, and confirmation that the boot warning remains visible.
