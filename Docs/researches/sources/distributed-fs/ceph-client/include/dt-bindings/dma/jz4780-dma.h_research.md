# sources/distributed-fs/ceph-client/include/dt-bindings/dma/jz4780-dma.h

## Purpose
Defines Ingenic JZ4780 DMA request IDs for device-tree DMA specifiers.

## Important APIs, Types, and Constants
Exports `JZ4780_DMA_*` constants for I2S, automatic DMA, SADC, UARTs, SSI, MSC, PCM, SMBus/I2C-style controllers, and DES engine TX/RX. Values are hardware request indexes, spanning from `0x4` through `0x2f`.

## Control Flow and State
No control flow. DMA channel allocation and request routing are handled by the Ingenic DMA driver.

## Dependencies and Integration Points
Self-contained header used by JZ4780 DTS device nodes in `dmas` properties and by the DMA provider mapping table.

## Risks and Test Signals
Wrong request IDs route transfers to the wrong peripheral. Test signals include DTS compilation, schema validation, and runtime DMA tests for audio, serial, storage, and crypto peripherals.
