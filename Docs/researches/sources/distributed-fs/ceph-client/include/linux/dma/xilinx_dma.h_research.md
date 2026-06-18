# sources/distributed-fs/ceph-client/include/linux/dma/xilinx_dma.h

## Purpose
This header exposes Xilinx VDMA channel configuration to DMAEngine clients and drivers. It is a narrow bridge between the generic DMAEngine API and Xilinx-specific video DMA features such as frame delay, frame parking, genlock, interrupt coalescing, external frame sync, and vertical flip.

## Important APIs, types, and functions
The central type is `struct xilinx_vdma_config`, with integer configuration fields for frame delay, genlock, master selection, frame count enable, park mode/frame, coalescing, delay counter, reset, external fsync, plus `bool vflip_en`. The exported function `xilinx_vdma_channel_set_config(struct dma_chan *dchan, struct xilinx_vdma_config *cfg)` applies the configuration to a DMAEngine channel.

## Control flow, state, and persistence
The header itself holds no state. The caller prepares a config object and passes it to the Xilinx DMA driver, which persists the values in channel registers or channel-private state. `reset` is an action-like field, so callers must treat the config as a command as well as a state description.

## Dependencies and integration points
It includes `linux/dma-mapping.h` and `linux/dmaengine.h`, and integrates with the generic `struct dma_chan` acquisition/submission path. Video pipelines, DRM, V4L2, and SoC display/capture drivers are likely clients.

## Risks and test signals
There is no compile-time range checking for frame numbers, coalescing, delay, or fsync source. Tests should validate that invalid channel pointers fail in the implementation, that reset does not leak resources, and that frame parking/genlock/vflip settings are reflected in hardware-visible behavior.
