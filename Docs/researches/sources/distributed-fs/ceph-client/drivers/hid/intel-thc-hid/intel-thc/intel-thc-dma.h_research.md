# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dma.h

Purpose: DMA data model for Intel THC. It defines PRD layout, channel IDs, pointer constants, per-channel configuration, aggregate DMA context, and exported DMA helper prototypes.

Important APIs/types: `enum thc_dma_channel` covers RXDMA1, RXDMA2, TXDMA, and SWDMA. `struct thc_prd_entry` is a bitfield hardware descriptor with shifted destination address, length, end-of-PRD, IOC, and status fields. `struct thc_dma_configuration` stores SG lists, PRD memory, register offsets, direction, table count, and max packet size. `struct thc_dma_context` groups all channels and SWDMA restore flags.

Control flow: callers set max packet sizes to enable channels, allocate buffers, configure hardware, exchange data, unconfigure, and release.

State and persistence: channel enablement and allocated DMA resources persist in the context. Temporary `rx_max_size_en` and `rx_int_delay_en` preserve I2C feature state during SWDMA.

Dependencies and integration: depends on Linux DMA mapping, sizes, and time constants. Included by `intel-thc-dev.h` and implemented by `intel-thc-dma.c`.

Risks: PRD bitfield layout must match hardware and compiler ABI assumptions. `PRD_ENTRIES_NUM` and `PRD_TABLES_NUM` constrain maximum transfer size and buffering depth. Address shifting assumes 1 KiB alignment.

Test signals: build-time layout sanity from compiler, DMA mapping tests on IOMMU/non-IOMMU systems, and transfer sizes spanning multiple SG entries.
