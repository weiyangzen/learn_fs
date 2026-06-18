# sources/distributed-fs/ceph-client/include/linux/dma/xilinx_dpdma.h

## Purpose
This small header defines peripheral configuration for Xilinx DPDMA transfers. It gives DMAEngine clients a typed way to mark a transfer as part of a video group.

## Important APIs, types, and functions
The only type is `struct xilinx_dpdma_peripheral_config`, containing `bool video_group`. There are no functions or inline helpers.

## Control flow, state, and persistence
No control flow is present. State is carried by the config struct and consumed by the DPDMA driver through `dma_slave_config.peripheral_config` or a similar driver-specific path.

## Dependencies and integration points
It depends only on `linux/types.h`. Integration is with Xilinx display DMA clients and the generic DMAEngine peripheral-configuration field.

## Risks and test signals
The risk is contract ambiguity: callers and the driver must agree on the lifetime and exact interpretation of `video_group`. Tests should cover grouped and non-grouped video transfers and verify that the driver rejects or ignores the option consistently when unsupported.
