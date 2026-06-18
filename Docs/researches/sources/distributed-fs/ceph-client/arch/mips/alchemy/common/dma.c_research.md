# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/dma.c

## Purpose
`dma.c` implements the older fixed-channel Au1000/Au1500/Au1100 DMA channel allocator. It loosely mirrors legacy `request_dma()`/`free_dma()` style APIs, maps device IDs to FIFO addresses and DMA modes, initializes channel IRQ numbers, and exports the channel table for classic Alchemy peripheral drivers.

## Important APIs, Types, And Functions
Exported symbols are `au1000_dma_table`, `request_au1000_dma()`, and `free_au1000_dma()`. `au1000_dma_read_proc()` formats a simple list of allocated channels for legacy proc use. `au1000_dma_init()` is an `arch_initcall()` that fills per-channel IRQ numbers based on CPU type. Static data includes `dma_dev_table` for primary devices, `dma_dev_table_bank2` for Au1100 SD controller devices, `DMA_CHANNEL_LEN`, and `au1000_dma_spin_lock`.

## Control Flow
Clients call `request_au1000_dma()` with a device ID, label, optional IRQ handler, IRQ flags, and IRQ cookie. The function validates the device ID against CPU capabilities, finds the first free `au1000_dma_table` entry, optionally requests the channel IRQ, fills channel MMIO base, device ID, label, FIFO address, mode flags, and initializes the hardware channel through `init_dma()`. `free_au1000_dma()` validates the channel, disables DMA, frees the IRQ if present, and marks the channel free.

At boot, `au1000_dma_init()` checks the CPU type, assigns the correct DMA interrupt base for Au1000/Au1500/Au1100, and logs initialization. Newer DBDMA-capable CPUs fall through without initializing this legacy table.

## State And Persistence
Persistent state is `au1000_dma_table[]`: device ownership, IRQ cookies, channel MMIO pointers, FIFO addresses, modes, labels, and IRQ numbers. Hardware channel registers are initialized/disabled through helper macros outside this file. Optional IRQ registrations persist until `free_au1000_dma()`.

## Dependencies And Integration Points
It depends on `asm/mach-au1x00/au1000_dma.h` for `struct dma_chan` and helper operations, Alchemy CPU type detection, fixed physical addresses for UART/AC97/USB/I2S/SD FIFOs, Linux IRQ APIs, and exported symbols consumed by legacy Alchemy drivers. It coexists with `dbdma.c` for later SoCs.

## Risks
The free-channel scan is not protected by `au1000_dma_spin_lock`, despite a global spinlock existing, so concurrent requests can race. Device IDs are normalized for bank2 before storing, which can obscure original Au1100 bank2 IDs. `request_au1000_dma()` requests the IRQ before fully initializing all channel fields, so handlers must not fire early. Unsupported CPU types silently skip IRQ setup; later requests on unsupported variants should be avoided by driver/platform selection. The legacy proc callback uses old procfs signature and direct `sprintf`.

## Test Signals
Build Au1000, Au1500, and Au1100 configs and confirm `"Alchemy DMA initialized"` appears only for supported fixed-DMA CPUs. Driver tests should request/free each device ID, verify IRQ base assignment, confirm FIFO/mode fields, exercise optional IRQ handlers, and check that all channels return `-ENODEV` when exhausted. Concurrency testing should look for duplicate channel allocation under parallel requests.
