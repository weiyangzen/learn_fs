# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm.h

## Purpose
Shared private declarations for i.MX PCM backends. It defines buffer sizing and the small interface used by SSI/SAI drivers to register either DMA-engine or FIQ PCM support.

## APIs, Types, and Functions
Defines default DMA buffer sizes such as `IMX_SSI_DMABUF_SIZE`/`IMX_DEFAULT_DMABUF_SIZE`, `struct imx_pcm_fiq_params` for FIQ initialization, and prototypes for `imx_pcm_dma_init()`, `imx_pcm_dma_exit()`, `imx_pcm_fiq_init()`, and `imx_pcm_fiq_exit()`.

## Control Flow, State, and Persistence
No control flow lives here. The FIQ params structure carries SSI base, IRQ, and DMA parameter pointers from a CPU DAI driver into the FIQ backend, while DMA-mode state is owned by the DMA-engine PCM core.

## Dependencies and Integration
Used by `imx-pcm-dma.c`, `imx-pcm-fiq.c`, and i.MX SSI/SAI CPU DAI drivers. Depends on platform devices and DMA slave config types from ALSA/DMA headers through including contexts.

## Risks and Test Signals
Risks are ABI drift between backend prototypes and CPU DAI callers, and buffer-size constants being too small or too large for particular latency/use cases. Test signals are successful builds of DMA and FIQ backends, component registration from CPU drivers, and ALSA buffer allocation matching expected size.
