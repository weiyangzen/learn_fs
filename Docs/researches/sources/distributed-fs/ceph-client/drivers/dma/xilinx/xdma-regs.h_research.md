# sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma-regs.h

## Purpose
`xdma-regs.h` defines the AMD/Xilinx XDMA register offsets, descriptor format, control/status bit masks, and helper macros consumed by `xdma.c`.

## Important APIs, Types, and Constants
The header defines a 64 KiB register space, up to four H2C and four C2H channels, descriptor-block constants, and `struct xdma_hw_desc`. Hardware descriptors are 32-byte little-endian records with control, byte count, source address, destination address, and next-descriptor pointer. `XDMA_DESC_CONTROL`, `XDMA_DESC_CONTROL_LAST`, and `XDMA_DESC_CONTROL_CYCLIC` construct descriptor control words with magic, adjacent descriptor count, and flags.

Channel register offsets cover identifier, control, status, completed descriptor count, alignment, interrupt enable, and SGDMA descriptor pointer registers. Macros such as `XDMA_CHAN_CHECK_TARGET` validate channel presence and direction by identifier magic. Interrupt register definitions cover user and channel interrupt enable/request/pending registers and vector-number tables.

## Control Flow and State Model
There is no runtime flow in this file, but its constants drive the `xdma.c` state machine. Descriptor block sizing determines allocation from DMA pools and limits cyclic descriptors to one adjacent block. Channel control masks decide which hardware conditions are treated as start bits, interrupts, and errors. Interrupt vector constants define how MSI-X vectors are packed four per register.

## Dependencies and Integration Points
The header expects Linux bit helpers such as `BIT`, `GENMASK`, and `FIELD_PREP` to be available through including C files. It is private to the Xilinx XDMA driver directory and integrated directly by `xdma.c`.

## Risks and Review Signals
Register definitions are hardware-contract sensitive. Any wrong offset, endian assumption, descriptor size, block alignment, or control-bit mask can produce silent DMA corruption. `XDMA_DESC_BLEN_MAX` subtracts `PAGE_SIZE` from a 28-bit max, so tests should include transfer splitting around that boundary. Review should validate channel magic values, vector packing, descriptor block boundary constraints, and error-mask coverage against current XDMA hardware documentation.
