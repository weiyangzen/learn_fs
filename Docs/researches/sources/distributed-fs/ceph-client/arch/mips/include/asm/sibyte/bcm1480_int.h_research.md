# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_int.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_int.h

### Purpose
`bcm1480_int.h` defines Broadcom/SiByte BCM1480 interrupt mapper source numbers, 128-bit high/low register layout, masks, CPU interrupt pin mappings, HyperTransport/LDT interrupt message fields, and vector prefixes.

### Important APIs, Types, And Functions
Important constants include `K_BCM1480_INT_SOURCES`, `_BCM1480_INT_HIGH`, `_BCM1480_INT_LOW`, source IDs for GPIO, PCI, cycle counters, timers, DMA channels, MACs, PMI/PMO, mailboxes, ECC, IO bus, perf/trace, watchdogs, HyperTransport/LDT, SMBus, PCMCIA, UARTs, and GPIO 4-15. Mask helpers include `_BCM1480_INT_MASK`, `_BCM1480_INT_MASK1`, `_BCM1480_INT_OFFSET`, `M_BCM1480_INT_*`, mapper targets `K_BCM1480_INT_MAP_*`, HT fields `S_/M_/V_/G_BCM1480_INT_HT_*`, HT message constants, and vector prefixes `M_BCM1480_HTVECT_*`.

### Control Flow
Interrupt-controller code uses source numbers to select high or low 64-bit registers, computes masks, maps sources to processor pins or special NMI/debug targets, and programs HT/LDT message fields for external interrupt delivery.

### State, Persistence, Dependencies, And Integration
State is BCM1480 interrupt mapper MMIO, 128-bit logical interrupt registers split across high/low addresses, CPU interrupt pins, mailbox state, and HT/LDT message routing. Dependency is `sb1250_defs.h` for bitfield helpers. Integration is with SiByte platform IRQ chips, PCI/HT, timers, MAC/UART/SMBus drivers, perf counters, watchdogs, and SMP/IPI style events.

### Risks
The low 64-bit register is offset unusually from the high register, and bit 0 high can summarize low bits; wrong offset math masks the wrong interrupts. Source numbers are SoC-specific despite similar families. HT field encodings must match external bridge/APIC expectations.

### Test Signals
Boot BCM1480-family platforms, validate all enabled IRQ sources, test timer/UART/MAC/PCI/HT interrupts, mailbox delivery, ECC/error interrupts, high/low mask writes, and interrupt affinity/pin mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_int.h -->
