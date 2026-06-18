# sources/distributed-fs/ceph-client/drivers/iio/adc/mcp320x.c

Purpose: this SPI IIO driver supports many Microchip ADCs: MCP3001/2/4/8, MCP3201/2/4/8, MCP3301, and MCP3550/1/3 variants. It exposes raw voltage channels, differential channel variants, and scale from a VREF regulator.

Important APIs, types, and functions: `struct mcp320x_chip_info` defines channel table, resolution, and conversion time. `struct mcp320x` stores SPI messages/transfers, regulator, lock, chip info, and DMA-aligned TX/RX buffers. `mcp320x_channel_to_tx_data()` builds channel-select command bytes. `mcp320x_adc_conversion()` performs optional conversion-start timing, SPI transfer, and per-model bit extraction. `mcp320x_read_raw()` provides raw and scale.

Control flow: probe selects chip info from SPI ID, sets channel tables, builds SPI messages for single-channel RX-only or multi-channel TX/RX devices, applies special MCP355x conversion-start and wake/reset handling, enables `vref`, and registers direct-mode IIO. Reads lock, determine model, perform conversion for the selected channel and differential mode, decode raw bits or signed/overrange MCP355x data, then return scale as VREF mV over resolution bits.

State and persistence: persistent state is SPI message layout, chip info, VREF regulator, and mutex. MCP355x devices have conversion timing and possible shutdown/wakeup behavior; the probe performs two dummy conversions to stabilize them.

Dependencies and integration points: it depends on SPI, regulator `vref`, IIO direct mode, OF and SPI ID matching. Channel arrays encode single-ended and differential combinations used by sysfs.

Risks and test signals: test all supported resolutions, SPI CPOL modes for MCP355x 24/25-bit reads, differential channel selection bytes, regulator scale, overrange/underrange handling, and single-channel devices with no MOSI. Risks are model-specific bit alignment, ignored errors from dummy conversions, and conversion time constants for slow delta-sigma parts.
