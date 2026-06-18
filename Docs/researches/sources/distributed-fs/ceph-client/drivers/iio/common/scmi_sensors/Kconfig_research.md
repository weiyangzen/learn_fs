# sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/Kconfig

Purpose: Kconfig menu for exposing ARM SCMI sensors as IIO devices.

Important symbols: `IIO_SCMI` is a tristate prompt depending on `ARM_SCMI_PROTOCOL` and selecting `IIO_BUFFER` and `IIO_KFIFO_BUF`. Help text states support for accelerometer and gyroscope sensors on SCMI-based platforms.

Control flow: selecting the symbol builds the SCMI IIO driver through the local Makefile.

State and persistence: no runtime state. It controls driver availability and required buffer support.

Dependencies and integration: integrates ARM SCMI protocol sensor discovery with the IIO subsystem. Kconfig indentation has spaces on some `depends/select/help` lines but remains semantically straightforward.

Risks and test signals: if buffer selections are wrong, probe would fail at kfifo setup. Test signals are Kconfig parse, module build under `ARM_SCMI_PROTOCOL`, and hidden/unavailable symbol when SCMI protocol support is absent.
