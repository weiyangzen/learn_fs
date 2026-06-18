# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_dbdma.h

**Purpose:** Defines the descriptor-based DMA controller used by later Alchemy SoCs, including hardware descriptor layouts, device ID assignments, channel state structures, and the exported DBDMA driver API.

**Important APIs/types/functions:** Exports `dbdma_global_t`, `au1x_dma_chan_t`, `au1x_ddma_desc_t`, `dbdev_tab_t`, `chan_tab_t`, descriptor command/status masks, device IDs for Au1550/Au1200/Au1300, custom ID helpers, descriptor width/type/status macros, `NUM_DBDMA_CHANS`, device/channel flags, and APIs such as `au1xxx_dbdma_chan_alloc()`, `au1xxx_dbdma_ring_alloc()`, `au1xxx_dbdma_put_source()`, `au1xxx_dbdma_put_dest()`, `au1xxx_dbdma_get_dest()`, `au1xxx_dbdma_start/stop/reset()`, `au1xxx_get_dma_residue()`, channel free/dump, descriptor put, device add/delete, and next-pointer translation.

**Control flow:** Drivers allocate a source/destination channel, allocate descriptor rings, enqueue source/destination buffers, start the channel, receive completion callbacks, drain descriptors, and stop/reset/free during teardown. Doorbell and descriptor-valid bits drive hardware execution.

**State and persistence behavior:** Software state is in channel tables, descriptor rings, spinlocks, callbacks, and device table entries maintained by the implementation. Hardware state lives in DBDMA global/channel registers and descriptor memory visible to DMA.

**Dependencies and integration points:** Depends on Linux DMA address types and spinlocks in consumers. Integrated by PSC, NAND, MAC, LCD, SD, AES, UART, USB, and memory-to-memory users on Au1550/Au1200/Au1300.

**Risks:** Descriptors must be 32-byte aligned and cache-coherent handling must match `SN/DN/DFN` bits. Wrong device IDs or widths can DMA to the wrong FIFO. Ring ownership, callbacks, and custom device IDs are easy to race or leak. The header contains a FIXME noting API placement concerns.

**Test signals:** Stress descriptor ring allocation/free, memory-to-memory transfers, each peripheral source/destination pair, callback ordering, residue reporting, descriptor alignment, non-coherent buffer handling, and error recovery after reset.
