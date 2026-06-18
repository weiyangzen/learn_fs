<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/omap-dma.h

## Purpose
This header exposes the legacy TI OMAP system DMA interface, register/bit definitions, channel parameter structures, platform data, and compatibility wrappers. It explicitly warns new code to use DMAEngine instead.

## Important APIs, types, and functions
It defines interrupt/status bits, channel control bits, data types, sync modes, port/addressing modes, FIFO/thread fields, sysconfig idle/reset bits, chain modes, priorities, errata bits, controller capability bits, register offsets/types, burst/endian/color/write/channel modes, `struct omap_dma_channel_params`, `struct omap_dma_lch`, `struct omap_dma_dev_attr`, `struct omap_dma_reg`, `SDMA_FILTER_PARAM()`, and `struct omap_system_dma_plat_info`. APIs include `omap_get_plat_info()`, `omap_set_dma_priority()`, `omap_request_dma()`, `omap_free_dma()`, USB-OMAP-gated channel setup/start/stop/position/status helpers, `omap_dma_running()`, and `omap_lcd_dma_running()`.

## Control flow
Legacy clients request a logical channel by device ID and callback, configure transfer/source/destination/sync/channel parameters, start DMA, receive callbacks for enabled IRQ/status bits, poll positions/status if needed, and free the channel. Platform code provides register maps, errata, capability display, clear/read/write callbacks, and DMAEngine slave maps.

## State and persistence
Runtime state is per-channel (`omap_dma_lch`) and controller platform data: channel ownership, callbacks, IRQ masks, saved CSR, chain state, register layout, errata, and hardware registers. Hardware DMA transfer state persists until stopped/reset.

## Dependencies and integration points
It depends on platform devices, OMAP architecture configs, DMAEngine slave maps, USB OMAP, framebuffer OMAP, and SoC-specific DMA controller implementations.

## Risks and test signals
Risks include legacy API use in new drivers, channel leaks, errata bit misconfiguration, register-width/stride mistakes, callback races during free, address mode/index errors, OMAP1 vs OMAP2 feature confusion, and IRQ mask mishandling. Test OMAP1/OMAP2+ compile paths, DMA request/free, transfer parameter programming, source/destination positions, IRQ callbacks, errata-specific behavior, USB/FB gated APIs, and concurrent channel use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-dma.h -->
