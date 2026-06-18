# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367_spi.c

## Purpose

`adxl367_spi.c` is the SPI transport wrapper for the ADXL367 core. It implements the chip's command-prefixed SPI register and FIFO protocol through a custom regmap bus and a FIFO callback.

## Important APIs, Types, and Functions

`struct adxl367_spi_state` stores the SPI device, preinitialized `spi_message` objects, transfer arrays, and DMA-aligned command buffers. `adxl367_read()`, `adxl367_write()`, and `adxl367_read_fifo()` are the custom regmap/FIFO operations. `adxl367_spi_probe()` builds the messages for write command `0x0A`, read command `0x0B`, and FIFO command `0x0D`, then calls the common probe.

## Control Flow

Probe allocates state, initializes three two-transfer SPI messages, creates a regmap with the custom bus, and invokes `adxl367_probe()` with the SPI IRQ. Register writes send command then address/data in a second transfer. Register reads send command/address then receive values. FIFO reads send the FIFO command then receive `fifo_entries * sizeof(__be16)` into the core buffer.

## State and Persistence Behavior

The wrapper caches only transfer descriptors and command bytes. Per-transfer lengths and data pointers are updated before each transaction while the common core serializes higher-level calls.

## Dependencies and Integration Points

It depends on SPI, regmap's custom bus API, IIO DMA alignment definitions, module tables, and the `IIO_ADXL367` namespace. Matching supports SPI ID and OF compatible `adi,adxl367`.

## Risks

The reusable `spi_message` objects assume no concurrent core calls mutate transfer descriptors at the same time; the core lock is therefore important. DMA alignment comments apply only to the command buffer explicitly aligned; transfer descriptors and RX buffers must continue to satisfy SPI controller requirements. Missing or invalid IRQs propagate to the common core.

## Test Signals

SPI logic is validated by probe, device ID read through command `0x0B`, reset write through command `0x0A`, FIFO burst command `0x0D`, and successful buffered capture without transfer length corruption.
