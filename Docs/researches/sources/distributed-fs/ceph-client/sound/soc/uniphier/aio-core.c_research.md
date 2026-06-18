<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-core.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-core.c

## Purpose
Common UniPhier AIO hardware programming library. It manages ring-buffer arithmetic, SoC glue IEC output, PLL programming, global chip initialization, per-substream mapping, port/SRC/DMA interface setup, digital volume, compressed stream type, DMA channel control, and hardware ring-buffer pointer synchronization.

## APIs, Types, and Functions
Exports many helpers consumed by `aio-cpu.c`, `aio-dma.c`, and `aio-compress.c`: `aio_rb_cnt()`, `aio_rb_space()`, `aio_iecout_set_enable()`, `aio_chip_set_pll()`, `aio_chip_init()`, `aio_init()`, `aio_port_reset()`, `aio_port_set_param()`, `aio_port_set_enable()`, `aio_port_get_volume()`, `aio_port_set_volume()`, `aio_if_set_param()`, `aio_oport_set_stream_type()`, `aio_src_reset()`, `aio_src_set_param()`, `aio_srcif_set_param()`, `aio_srcch_set_param()`, `aio_srcch_set_enable()`, `aiodma_ch_set_param()`, `aiodma_ch_set_enable()`, `aiodma_rb_set_threshold()`, `aiodma_rb_set_buffer()`, `aiodma_rb_sync()`, IRQ test/clear helpers, and internal pointer load/store routines.

## Control Flow, State, and Persistence
Chip init powers audio PLLs, configures external MCLK output, input source selectors, and address-extension mode. Per-substream init writes resource maps for ring buffer, DMA channel, input/output interfaces, ports, and converter paths based on `swm`. PCM port setup validates channels/rates/formats, chooses PLL/divider routing, configures pass-through or PCM validity, and enables port masks. SRC setup handles selected output rates. DMA setup configures channel address modes and ring-buffer start/end/thresholds; ring synchronization reads hardware pointers, updates software offsets, totals, and hardware producer/consumer pointers. Volume state is applied by fade slope/target registers.

## Dependencies and Integration
Depends heavily on `aio-reg.h` register definitions, regmap MMIO, `aio.h` topology/spec structures, ALSA PCM params, bitfield helpers, and IEC61937 type definitions. It is the shared implementation beneath CPU DAI, PCM DMA, and compressed paths.

## Risks and Test Signals
Risks include many `regmap_write/update_bits` return values ignored, ring-buffer arithmetic reserving eight bytes without documenting hardware constraints, pointer-load delay loops using repeated reads instead of timeouts, limited PLL frequencies, defaulting SRC rates to 48 kHz for unsupported rates, volume slope divide behavior at zero sample rate, and complex mapping tables from SoC specs. Test signals are PLL A/F 36.864/33.8688 MHz programming, 2/6/8 channel PCM, I2S/left/right-justified formats, pass-through SPDIF, SRC 32/44.1/48 kHz, volume fade, ring wraparound, IRQ threshold behavior, and LD11/PXs2 address-extension variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-core.c -->
