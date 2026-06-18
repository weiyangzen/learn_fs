# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_spi.c

Purpose: SPI-bus wrapper for AD7606-family devices. It supplies block-read, register-read/write, software-mode setup, scan-mask validation, and optional SPI offload/DMA streaming hooks to the common AD7606 core.

Important APIs, types, and functions: `struct spi_bus_data` stores SPI offload objects and optimized transfer state. `ad7606_spi_probe()` resolves a `struct ad7606_bus_info` and calls `ad7606_probe()`. Read paths are `ad7606_spi_read_block()`, `ad7606_spi_read_block14to16()`, and `ad7606_spi_read_block18to32()`. Register paths are `ad7606_spi_reg_read()`, `ad7606_spi_reg_write()`, `ad7616_spi_rd_wr_cmd()`, and `ad7606b_spi_rd_wr_cmd()`. Offload support is implemented by `ad7606_spi_offload_probe()`, buffer enable/disable callbacks, and SPI offload trigger ops.

Control flow: probe maps each compatible to chip info plus bus ops. Standard SPI reads transfer all channel samples and convert 16-bit big-endian data to CPU order, while AD7607 and AD7608/7609/7606C-18 use 14-bit or 18-bit transfers into 16/32-bit storage. Software-mode register access performs a command transfer followed by a data transfer for reads or one 16-bit command/data write. Offload probe is attempted by the core; if no offload provider exists it returns success without enabling offload, otherwise it registers a data-ready trigger, requests RX stream DMA, installs DMAengine buffer ops, and marks `st->offload_en`. Offload buffer enable optimizes an RX stream message, enables the data-ready trigger, and starts conversion PWM swing; disable stops PWM, disables trigger, and unoptimizes the message.

State and persistence behavior: per-bus offload state is devm-managed in `st->bus_data`. Register writes configure volatile ADC mode, single DOUT, ranges, and oversampling through the common core. Offload requires all physical channels in the scan mask because the DMA stream cannot demux partial channel sets.

Dependencies and integration points: depends on SPI core, SPI offload provider/consumer APIs, IIO DMAengine buffer, PWM helpers exported by the core, DT binding trigger event constants, and `ad7606.h`. It imports `IIO_AD7606` and `IIO_DMAENGINE_BUFFER`.

Risks: offload path has strict scan-mask semantics and assumes hardware-compatible storagebits. Register command encodings differ between AD7616 and AD7606B/C; wrong bus-info pairing breaks software mode. The standard `spi_read()` block conversion mutates the receive buffer in place. Offload failure unwinding must keep optimized messages and triggers balanced.

Test signals: run direct and buffered reads for 16/14/18-bit devices; exercise software-mode register reads/writes for AD7616 and AD7606B/C; test no-offload fallback, offload probe success, offload buffer enable/disable, and invalid partial scan masks; validate single-DOUT software setup.
