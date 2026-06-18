# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_dma.h

Purpose: defines SB1250 Ethernet/serial DMA and generic data-mover register and descriptor bitfields. It is the contract between network/serial/data-mover drivers and the descriptor formats consumed by the DMA engines.

Important APIs/types/functions: there are no C functions or structs. Key macro groups cover `DMA_CONFIG0/1` control bits, descriptor base/current/count fields, receive drop counters, Ethernet/serial descriptor doubleword A/B layouts, Ethernet RX/TX status and option encodings, serial RX/TX status/options, data-mover descriptor base/current/partial-result registers, CRC/TCP checksum definition registers, and data-mover descriptor source/destination direction and checksum/CRC options.

Control flow: drivers construct descriptor rings, program descriptor base/count registers, enable DMA channels, then poll or handle interrupts using status bits. Descriptor control flow is split across valid/address/size/status fields and interrupt flags; data-mover descriptors additionally encode source/destination direction, zeroing, prefetch, L2 hints, read/write backoff, CRC, and TCP checksum behavior.

State and persistence: descriptor rings live in DMA-visible memory owned by drivers. The channel registers and current descriptor pointers are hardware state; status bits are written by hardware and consumed by interrupt/poll paths.

Dependencies and integration: depends on `sb1250_defs.h`; feature gates expose later pass/BCM1480 additions such as enhanced addressing, pause/status bits, VLAN/CRC flags, partial CRC/checksum results, and data-mover checksum options. It integrates with `sb1250_regs.h`/`bcm1480_regs.h` address macros and MAC/serial drivers.

Risks and test signals: address masks, ring sizes, and descriptor ownership bits are high risk because mistakes can DMA to wrong memory. `M_DMA_DSCRB_STATUS` is duplicated, and several bits have different meanings for read versus write or RX versus TX. Test signals include compile coverage for pass1/pass2/pass3 feature gates, descriptor layout unit checks, DMA ring wrap tests, Ethernet RX/TX checksum/VLAN tests, serial DMA transfer tests, and data-mover CRC/checksum validation on hardware.
