# sources/distributed-fs/ceph-client/include/linux/misc/keba.h

## Purpose
Defines KEBA auxiliary-device wrapper structures for I2C, SPI, fan, battery, and UART subdevices.

## Important APIs/Types
`keba_i2c_auxdev`, `keba_spi_auxdev`, `keba_fan_auxdev`, `keba_batt_auxdev`, and `keba_uart_auxdev` each embed `auxiliary_device` plus an IO resource. I2C/SPI wrappers carry board-info arrays and counts; UART carries an IRQ.

## Control Flow
No functions are defined. Parent drivers instantiate wrappers and register auxiliary devices; child drivers recover wrapper data during probe.

## State And Persistence
Parent-owned wrapper state persists while the auxiliary device is registered. Resource, board-info, and IRQ lifetimes must cover child usage.

## Dependencies And Integration Points
Depends on the auxiliary bus and I2C/SPI board-info declarations. Integrates KEBA parent drivers with I2C, SPI, fan, battery, and serial children.

## Risks
Wrong wrapper casting, invalid board-info lifetime, overlapping resources, missing UART IRQ propagation, and release-order mistakes.

## Test Signals
Auxiliary registration/probe/remove, resource mapping, I2C/SPI enumeration, UART IRQ handling, and clean unregister ordering.
