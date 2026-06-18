# sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/Kconfig

Purpose: Kconfig declaration for the common TDK-InvenSense timestamp helper library used by InvenSense IIO sensor drivers.

Important symbols: `IIO_INV_SENSORS_TIMESTAMP` is a hidden tristate with no prompt in this file. Device-specific drivers select it when they need the timestamp estimation helpers.

Control flow: users do not normally enable this directly. Kconfig selection by a concrete driver causes `inv_sensors_timestamp.o` to build.

State and persistence: no runtime state here; it controls helper-library availability.

Dependencies and integration: the helper is intended to be shared by InvenSense FIFO/timestamp-capable sensor drivers and is built from the local Makefile.

Risks and test signals: because the symbol is hidden, missing `select` lines in users produce unresolved references. Test signals are Kconfig coverage from all users and successful modpost for drivers importing `IIO_INV_SENSORS_TIMESTAMP` symbols.
