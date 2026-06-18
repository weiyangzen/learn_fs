# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/seeq.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/seeq.h

### Purpose
`sgi/seeq.h` defines platform data for the SGI SEEQ Ethernet driver when attached through HPC3.

### Important APIs, Types, And Functions
The exported type is `struct sgiseeq_platform_data`, containing an `hpc3_regs` pointer, IRQ number, and Ethernet MAC address buffer sized by `ETH_ALEN`.

### Control Flow
Platform setup fills this structure and passes it to the SEEQ driver, which then uses the HPC3 register pointer and IRQ to drive Ethernet DMA/control.

### State, Persistence, Dependencies, And Integration
State is platform-provided hardware pointer, interrupt line, and MAC address. Dependencies include Ethernet address definitions and `hpc3.h`. Integration is SGI onboard Ethernet platform-device setup.

### Risks
An incorrect HPC pointer or IRQ breaks network I/O; an unset or invalid MAC address creates duplicate or unusable Ethernet identity.

### Test Signals
Probe the SEEQ driver, verify MAC address, transmit/receive traffic, IRQ delivery, and HPC3 DMA interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/seeq.h -->
