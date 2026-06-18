# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367.h

## Purpose

`adxl367.h` is the private interface between the ADXL367 transport wrappers and the shared IIO core. It keeps bus-specific code out of `adxl367.c` while allowing the core to use a transport-specific FIFO command.

## Important APIs, Types, and Functions

`struct adxl367_ops` currently contains one callback, `read_fifo(void *context, __be16 *fifo_buf, unsigned int fifo_entries)`. `adxl367_probe()` is declared as the common probe entry and accepts a device, ops table, opaque bus context, regmap, and IRQ number.

## Control Flow

I2C and SPI probes allocate their bus state, create a regmap, construct an `adxl367_ops` table, and call `adxl367_probe()`. The core stores the context and calls `ops->read_fifo()` only from the IRQ FIFO drain path.

## State and Persistence Behavior

The header owns no state. It defines the callback contract: the context is transport-owned and remains valid for the lifetime of the devm-managed IIO device.

## Dependencies and Integration Points

The file includes `linux/types.h` for `__be16` and forward declares `struct device` and `struct regmap`. The exported probe symbol is namespaced as `IIO_ADXL367` in the core and imported by bus modules.

## Risks

Any extension of `struct adxl367_ops` must update both bus wrappers. The FIFO callback uses entry counts rather than byte counts; callers and implementations must preserve that unit.

## Test Signals

Build tests should verify both I2C and SPI wrappers compile against this header, import the namespace, and pass a non-null `read_fifo` implementation.
