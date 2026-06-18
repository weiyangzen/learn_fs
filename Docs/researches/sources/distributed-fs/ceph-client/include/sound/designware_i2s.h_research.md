# sources/distributed-fs/ceph-client/include/sound/designware_i2s.h

## Purpose
This header defines platform glue structures for Synopsys DesignWare I2S controllers used by ALSA/ASoC drivers.

## Important APIs, Types, and Constants
`struct i2s_clk_config_data` describes channel count, sample rate, and data width. `struct i2s_platform_data` contains capability flags, channel/fifo metadata, clock configuration callback, filter functions for DMA channel acquisition, optional playback/capture DMA data, optional I2S init hook, and quirks. `struct i2s_dma_data` stores DMA address, address width, max burst, and filter data. Constants include DMA register offsets `I2S_RXDMA`/`I2S_TXDMA` and max channel support markers from stereo to 7.1.

## Control Flow
Platform or glue code provides pdata to the DesignWare I2S driver. The driver invokes the init hook, configures clocks using `i2s_clk_cfg`, requests DMA channels using filters/data, and sets channel support/fifo handling based on pdata fields.

## State and Persistence
The structs describe controller capabilities and board wiring; runtime stream state is in the DesignWare driver and hardware registers. DMA channel state is external to this header.

## Dependencies and Integration Points
It depends on `linux/dmaengine.h` and `linux/types.h`. Integration points include DMAengine, ASoC DAI drivers, clock providers, and platform firmware data.

## Risks and Edge Cases
Incorrect FIFO depth or DMA burst/address-width values cause underruns/overruns. Capability flags and channel counts must match IP configuration. Callback pointers should be NULL-safe and must not sleep in inappropriate contexts if called from stream setup paths.

## Test Signals
Playback and capture DMA startup, all advertised channel counts, clock reconfiguration for multiple rates/widths, and underrun/overrun stress tests validate this contract.
