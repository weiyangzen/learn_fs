# sources/distributed-fs/ceph-client/drivers/iio/gyro/Makefile

## Purpose
Build rules for IIO gyroscope drivers and composite modules.

## Important APIs, Types, And Functions
Rules map Kconfig symbols to objects: ADIS/ADXRS single-object drivers, `bmg160_core.o` plus bus shims, `fxas21002c_core.o` plus bus shims, `hid-sensor-gyro-3d.o`, composite `mpu3050.o`, composite `itg3200.o`, `ssp_gyro_sensor.o`, and composite `st_gyro.o` plus ST bus shims.

## Control Flow
Kbuild includes objects according to `obj-$(CONFIG_...)`. Composite module members are listed with `mpu3050-objs`, `itg3200-y`, `itg3200-$(CONFIG_IIO_BUFFER)`, `st_gyro-y`, and `st_gyro-$(CONFIG_IIO_BUFFER)`.

## State And Persistence
No runtime state. Build output determines module names and whether buffer helpers are linked into composite modules.

## Dependencies And Integration Points
Tightly coupled to `drivers/iio/gyro/Kconfig`; the module split must match exported symbols in core and bus files, including BMG160, FXAS21002C, MPU3050, ITG3200, and ST gyros.

## Risks
Kconfig/Makefile drift can create unresolved symbols or missing bus modules. Conditional buffer object inclusion means buffer APIs must stay guarded in headers and call sites.

## Test Signals
Compile with buffer enabled and disabled, compile with each bus backend as built-in and module, and confirm module names match Kconfig help text.
