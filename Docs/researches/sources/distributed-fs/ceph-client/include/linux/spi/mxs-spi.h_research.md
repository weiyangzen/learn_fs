<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mxs-spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/mxs-spi.h

Purpose: This header defines Freescale i.MX23/i.MX28 SSP/SPI register offsets, bitfields, helpers, and shared controller state.

Important APIs/types/functions: Register macros cover SSP control, command, transfer/block size, timing, data, response, and status registers with old/new offset differences via `ssp_is_old()`. `BF_SSP()` builds field values. `enum mxs_ssp_id` distinguishes IMX23 and IMX28. `struct mxs_ssp` stores device, MMIO base, clock, clock rate, device ID, DMA channel/direction, and PIO command words. `mxs_ssp_set_clk_rate()` programs clock rate.

Control flow: Controller code uses variant-aware register offsets, builds control words, configures clocks/timing, selects DMA or PIO, and monitors status/interrupt bits for transfer completion or errors.

State and persistence: Persistent controller state includes MMIO registers, clock rate, DMA direction/channel, and cached PIO words. The struct tracks enough state to program both SPI and related SSP modes.

Dependencies/integration: Depends on DMA engine, clocks, MMIO, SPI/MMC-capable SSP hardware, and SoC variant knowledge.

Risks and test signals: Risks include using wrong register map for IMX23 vs IMX28, bad clock divisors, DMA direction mismatch, FIFO/status error mishandling, and CRC/timeout bits crossing SPI/MMC modes. Test with PIO and DMA transfers, clock-rate changes, both SoC variants, FIFO under/overflow handling, and timeout/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mxs-spi.h -->
