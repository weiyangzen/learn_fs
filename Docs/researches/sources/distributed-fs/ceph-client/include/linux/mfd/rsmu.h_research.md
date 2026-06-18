# sources/distributed-fs/ceph-client/include/linux/mfd/rsmu.h

## Purpose

This 38-line header is the shared core interface for Renesas Synchronization Management Unit devices, covering ClockMatrix, Sabre, and SnowLotus variants.

## Important APIs, Types, and Functions

It defines maximum bus transfer sizes, `enum rsmu_type` values for supported device families, and `struct rsmu_ddata`, which carries the backing device, regmap, serialization mutex, type, and current page for I2C/SPI driver use.

## Control Flow

No executable flow is defined. Subdevices receive `rsmu_ddata`, lock around multi-register transactions, use regmap for bus access, and rely on the parent to manage page selection.

## State and Persistence Behavior

`struct rsmu_ddata` holds runtime shared state. The mutex serializes bus/page-sensitive operations, and `page` tracks parent-driver paging state; hardware clock/synchronization state remains in the SMU.

## Dependencies and Integration Points

The header integrates Renesas MFD parent drivers with clock/PTP/synchronization child devices using Linux `device`, `regmap`, and `mutex` infrastructure.

## Risks and Edge Cases

Missing the lock around paged accesses can interleave transactions from subdevices and target the wrong page. Transfer sizes must respect the 255-byte read/write limits.

## Test Signals

Build coverage for I2C/SPI RSMU drivers, concurrent subdevice access tests, page-switch regression tests, and max-length regmap transfer checks.
