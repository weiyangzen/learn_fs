# sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551_core.h

Purpose: public contract for MMA955x shared core helpers and application identifiers.

Important APIs/types/functions: defines app ids for VERSION, GPIO, AFE, TILT, SLEEP_WAKE, PEDOMETER, RSC, and NONE; reset mask `MMA9551_RSC_PED`; autosuspend delay; `enum mma9551_gpio_pin`; and the `MMA9551_ACCEL_CHANNEL(axis)` channel macro. It declares all exported mailbox, GPIO, power, accelerometer, sleep, and reset helpers implemented in `mma9551_core.c`.

Control flow: MMA9551 and MMA9553 frontend drivers include this header, define their IIO channels with the accel macro, and call exported helpers while holding their device mutex.

State and persistence: no state is stored here, but constants encode persistent firmware application registers and GPIO pin numbering used by device configuration.

Dependencies and integration points: depends on I2C client and IIO channel types from includers. Exported functions live in namespace `IIO_MMA9551`.

Risks: the channel macro assumes `IIO_ACCEL`, modifiers, and `IIO_CHAN_INFO_*` symbols are already included. The API comments requiring external locking are in the C file rather than enforced by type or lockdep.

Test signals: build coverage of both frontends, namespace import resolution, and compile-time validity of app ids, GPIO enum, and accel-channel macro.
