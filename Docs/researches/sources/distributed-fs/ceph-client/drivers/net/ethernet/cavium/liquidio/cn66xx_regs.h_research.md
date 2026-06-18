# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_regs.h

## Purpose
This header defines the CN6XXX/CN66XX LiquidIO register map: PCI config offsets, BAR0 window registers, IQ/OQ CSRs, global packet controls, DMA counters, interrupt masks, BAR1 index addresses, DPI registers, CIU reset registers, MIO/PTP registers, QLM/reset boot registers, and LMC reset constants.

## Important APIs, Types, And Functions
Macro families include `CN6XXX_SLI_IQ_*`, `CN6XXX_SLI_OQ_*`, `CN6XXX_DMA_*`, `CN6XXX_SLI_INT_*`, `CN6XXX_INTR_*`, `CN6XXX_BAR1_REG()`, `CN6XXX_DPI_*`, `CN6XXX_CIU_*`, and `CN6XXX_MIO_*`. It also defines endian-dependent `CN6XXX_INPUT_CTL_MASK` and composed masks for packet, DMA, PCIe-data, MIO, MAC, error, and total interrupt groups.

## Control Flow
There is no executable flow. CN66XX and CN68XX setup code uses these constants to program queue rings, interrupt coalescing, DPI, reset, BAR1 windows, and port routing.

## State And Persistence
State is represented by hardware registers addressed through the macros. The header contains no runtime allocation or persistence.

## Dependencies And Integration Points
The header depends on kernel bit macros and is included by CN66XX/CN68XX device implementation files. CN68XX-specific headers extend the map rather than replacing it.

## Risks
Stride and offset macros are central to DMA queue programming; incorrect use can corrupt unrelated CSRs. `CN6XXX_DPI_SLI_PRTX_CFG(port)` advances by `0x10` while separate constants show port0/port1 at `0x900` and `0x908`; this may reflect hardware layout or a suspicious stride and should be verified against documentation. Interrupt masks include broad error bits and data bits; handlers must clear exactly the bits they serviced. Endian-dependent input control must be validated on big-endian builds.

## Test Signals
Compile all users, compare generated addresses against hardware docs, exercise queue setup for multiple IQ/OQ indices, validate interrupt summary/mask behavior, BAR1 index programming, DPI setup, and reset register access on CN66XX hardware or emulation.
