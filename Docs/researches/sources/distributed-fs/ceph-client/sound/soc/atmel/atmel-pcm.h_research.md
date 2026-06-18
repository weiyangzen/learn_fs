# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm.h

## Purpose
This header defines the shared contract between Atmel SSC DAI code and the two PCM transport implementations, PDC and DMAengine.

## Important APIs, Types, And Functions
Important types are `struct atmel_pdc_regs`, `struct atmel_ssc_mask`, and `struct atmel_pcm_dma_params`. It defines `ATMEL_SSC_DMABUF_SIZE`, raw SSC access macros `ssc_readx()`/`ssc_writex()`, and conditional declarations/stubs for `atmel_pcm_pdc_platform_register()` and `atmel_pcm_dma_platform_register()`.

## Control Flow
No runtime control flow in the header. Conditional compilation selects real registration functions when the corresponding config is enabled, otherwise stubs return success.

## State And Persistence
The structures describe persistent per-stream integration state: SSC device, PDC register offsets, status masks, substream pointer, transfer size, and interrupt callback. Actual lifetime is managed by SSC DAI and PCM callbacks.

## Dependencies And Integration Points
It depends on `linux/atmel-ssc.h` and is included by SSC DAI plus both PCM implementations. It is the main ABI-like internal bridge between the DAI's SSC register programming and the PCM transport's buffer movement.

## Risks And Test Signals
Risk is stale or inconsistent mask/register definitions causing one transport to disable or acknowledge the wrong hardware state. Test signals are both PDC and DMA variants building, SSC streams setting/clearing `dma_intr_handler` correctly, and injected overrun/underrun handling through the shared callback.
