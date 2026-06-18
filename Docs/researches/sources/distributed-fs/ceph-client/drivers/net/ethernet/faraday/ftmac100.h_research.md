# sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftmac100.h

## Purpose
This header defines the FTMAC100 hardware contract used by `ftmac100.c`: register offsets, interrupt/status/control bits, MDIO command fields, and aligned RX/TX DMA descriptor layouts.

## Important APIs, Types, and Functions
The key exported local types are `struct ftmac100_txdes` and `struct ftmac100_rxdes`, each aligned to 16 bytes and made of four words. The first two words hold status/control flags, the third holds a hardware buffer address, and the fourth is explicitly unused by hardware and used by the C driver as private scratch. Macro groups describe `FTMAC100_OFFSET_*` registers, `FTMAC100_INT_*` ISR/IMR bits, interrupt coalescing/timer fields, DMA burst control, `FTMAC100_MACCR_*`, MDIO fields, and descriptor flags such as `FTMAC100_TXDES0_TXDMA_OWN`, `FTMAC100_TXDES1_EDOTR`, `FTMAC100_RXDES0_RXDMA_OWN`, `FTMAC100_RXDES0_FRS`, and `FTMAC100_RXDES1_EDORR`.

## Control Flow
The header has no executable control flow, but it defines the protocol for the source file. Rings are terminated by `EDOTR` or `EDORR`; DMA ownership is represented by the high bit of descriptor word 0; RX frame boundaries use FRS/LRS; TX frame boundaries use FTS/LTS; and MDIO access is issued through PHYCR/PHYWDATA bitfields.

## State and Persistence
The only state represented here is volatile hardware state in MMIO registers and DMA descriptors. There is no persistent state. The descriptor `txdes3` and `rxdes3` fields are typed as `unsigned int` even though the driver stores kernel pointers there; this is a structural portability concern.

## Dependencies and Integration Points
The file is private to the Faraday driver. It depends on kernel fixed-width endian types such as `__le32` being available through including C files. Its definitions integrate the platform driver with the Ethernet MAC, DMA engine, and MII management block.

## Risks
Bit definitions must match the hardware manual exactly; mistakes cause silent DMA corruption, interrupt loss, or packet filtering errors. The 11-bit buffer-size masks enforce the driver's `0x7ff` size limits. Pointer scratch fields are unsafe if built for an ABI where `sizeof(void *) > sizeof(unsigned int)`.

## Test Signals
Compile coverage catches missing definitions. Runtime validation should focus on descriptor ring wrap, interrupt mask behavior, MDIO read/write, multicast hash programming, and RX/TX ownership transitions.
