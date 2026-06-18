# sources/distributed-fs/ceph-client/drivers/spi/spi-butterfly.c

## Purpose
Implements a parport-to-SPI adapter driver for the AVR Butterfly board and its DataFlash device. It demonstrates a concrete SPI bitbang controller built on the `spi_bitbang` framework and parallel-port pin manipulation.

## Important APIs, Types, And Functions
`struct butterfly` embeds `struct spi_bitbang`, stores the parport and pardevice, tracks the last data byte driven to the port, records created SPI devices, and holds two `spi_board_info` entries. Low-level bitbang hooks are `setsck()`, `setmosi()`, `getmiso()`, and `butterfly_chipselect()`. `butterfly_txrx_word_mode0()` wires `bitbang_txrx_be_cpha0()` from `spi-bitbang-txrx.h` into SPI mode 0. Parport lifecycle is handled by `butterfly_attach()` and `butterfly_detach()`.

## Control Flow
When a parport matches, `butterfly_attach()` refuses additional instances because of a single global pointer, allocates an SPI host, configures bus number 42 and two chip selects, wires bitbang callbacks, registers and claims a parport device, powers and resets the Butterfly through data/control pins, starts the SPI bitbang controller, and creates an `mtd_dataflash` SPI child on chip select 1 with partition data. Detach stops the bitbang controller, powers off VCC, releases/unregisters the parport device, and drops the SPI controller reference.

## State And Persistence
The global `butterfly` pointer enforces a single active adapter and persists until detach. `lastbyte` mirrors the parallel port data register state for SCK/MOSI/VCC/reset updates. Child SPI devices and MTD partitions exist while the bitbang controller is registered. Partition definitions and flash platform data are static module data.

## Dependencies And Integration Points
The driver depends on Linux parport, SPI core, `spi_bitbang`, `spi-bitbang-txrx.h`, SPI flash platform data, and MTD partitions. It registers as a `parport_driver` named `spi_butterfly`, creates an SPI controller, and instantiates an `mtd_dataflash` child device. Documentation is referenced in `Documentation/spi/butterfly.rst`.

## Risks And Edge Cases
There is no hardware discovery; attach assumes the custom cable and Butterfly are present. The single global prevents more than one adapter. Timing uses no delay by default, so it relies on parport operations being slow enough. Power/reset sequencing is board-specific. The code uses old-style board-info instantiation and static partitioning; modern systems may prefer device tree or software nodes. Failure cleanup must unwind parport claim, power, and SPI host references in the right order.

## Test Signals
Test attach/detach with the actual parallel-port cable, logic analyzer mode-0 waveforms, DataFlash device creation, MTD partition registration, power/reset pin behavior, and failure paths when parport claim or `spi_bitbang_start()` fails. Functional signal is successful reads from the DataFlash child at the configured speed.
