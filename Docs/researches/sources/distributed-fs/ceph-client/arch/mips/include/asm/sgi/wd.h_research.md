# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/wd.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/wd.h

### Purpose
`sgi/wd.h` defines platform data for SGI WD93 SCSI controllers attached through HPC3.

### Important APIs, Types, And Functions
The exported type is `struct sgiwd93_platform_data`, containing controller unit, IRQ, pointer to `struct hpc3_scsiregs`, and pointer to external WD registers.

### Control Flow
Board setup provides this platform data to the WD93 SCSI driver; the driver uses the HPC3 SCSI DMA register block and external register pointer to issue SCSI commands and handle IRQs.

### State, Persistence, Dependencies, And Integration
State is platform wiring information and SCSI/HPC3 MMIO state, with persistent storage only in attached SCSI devices outside this header. Dependency is `hpc3.h`. Integration is SGI onboard SCSI platform device setup.

### Risks
Wrong register pointers or IRQs can corrupt DMA or hang the SCSI bus. Unit numbering must match physical controller wiring.

### Test Signals
Probe both possible WD93 units, enumerate SCSI disks, run read/write stress, disconnect/reselect tests, and IRQ/DMA error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/wd.h -->
