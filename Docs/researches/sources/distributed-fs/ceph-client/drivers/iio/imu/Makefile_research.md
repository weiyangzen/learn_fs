# sources/distributed-fs/ceph-client/drivers/iio/imu/Makefile

Purpose: Kbuild rules for IIO IMU drivers and the common ADIS library.

Important APIs/types/functions: Maps ADIS and other IMU Kconfig symbols to objects. Builds `adis_lib.o` from `adis.o` plus optional `adis_trigger.o` and `adis_buffer.o` when `CONFIG_IIO_ADIS_LIB_BUFFER` is enabled. Recurses unconditionally into several IMU subdirectories with `obj-y +=`.

Control flow: Build-time object selection only.

State and persistence: No runtime state. Build products depend on Kconfig selections.

Dependencies and integration points: Integrates with ADIS namespace/library consumers, FXOS8700 core/transports, KMX61, SMI240, and nested IMU driver directories.

Risks: ADIS library object composition must match exported symbols used by selected drivers. Unconditional subdirectory traversal relies on child Makefiles to gate objects correctly.

Test signals: Build selected IMU modules, especially ADIS with buffer enabled/disabled, and verify module dependency metadata for `adis_lib`.
