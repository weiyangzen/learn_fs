# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/hpc3.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/hpc3.h

### Purpose
`sgi/hpc3.h` maps the SGI HPC3 peripheral controller: PBUS DMA channels, SCSI DMA, SEEQ Ethernet DMA/control, interrupt status, EEPROM, PROM, RTC, battery-backed RAM, and peripheral timing/config registers.

### Important APIs, Types, And Functions
Key types are `struct hpc_dma_desc`, `struct hpc3_pbus_dmacregs`, `struct hpc3_scsiregs`, `struct hpc3_ethregs`, and `struct hpc3_regs`. Important macros cover DMA descriptor flags (`HPCDMA_*`), PBUS DMA control, SCSI byte count/control/config, Ethernet RX/TX control and descriptors, IRQ status bits, GIO misc/endian bits, EEPROM/PROM controls, DMA/PIO timing fields, chip base addresses, globals `hpc3c0`/`hpc3c1`, and `sgihpc_init`.

### Control Flow
Drivers build descriptor chains, program descriptor pointers and byte counts, set control bits to start DMA, inspect status/interrupt registers, and clear/reset channels. Ethernet and SCSI drivers access external device registers through HPC3 windows and use DMA completion/status bits for progress.

### State, Persistence, Dependencies, And Integration
State is volatile controller MMIO, DMA descriptors in memory, FIFO pointers, EEPROM/PROM/RTC/BBRAM contents, and global mapped-controller pointers. Dependencies include Linux types and page definitions. Integration is with SGI SCSI, Ethernet, parallel/PBUS device drivers, interrupt handling, DMA mapping, and early platform initialization.

### Risks
Descriptor ownership and endian bits must match CPU/device expectations. Some IRQ status bits require reading two different registers due to hardware quirks. Volatile register layout and large padding must stay exact; word access to subdevices can have side effects.

### Test Signals
Boot IP22/IP28-style systems, exercise SCSI and SEEQ Ethernet DMA under load, test PBUS devices, validate EEPROM/RTC access, interrupt status clearing, DMA endian modes, and descriptor ring wrap/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/hpc3.h -->
