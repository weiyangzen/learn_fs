# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_iio.h

Purpose: central header for the MPU6050-family driver. It defines register maps, supported chip enums, state/config structs, register constants, scan indices, filter/FSR enums, frequency macros, and cross-file prototypes.

Important types: `struct inv_mpu6050_reg_map` abstracts variant register addresses. `enum inv_devices` lists supported MPU/ICM/IAM parts. `struct inv_mpu6050_chip_config` caches current clock, FSR, LPF, enabled sensors, FIFO bits, divider, user control, and WoM threshold. `struct inv_mpu6050_hw` carries WHOAMI, name, register map, defaults, FIFO size, temp conversion, and startup times. `struct inv_mpu6050_state` is the global driver state for IIO, trigger, mux, orientation, regmap, timestamp, regulators, magnetometer, suspend masks, data buffer, and IRQ timestamp.

Important macros and APIs: sensor masks, register bit definitions, FIFO size constants, temp conversions, frequency/divider conversion helpers, scan indices, FSR/filter enums, and prototypes for FIFO, trigger, engine switching, ACPI, and core probe.

Integration: included by every MPU6050 source file and exported to transport modules. It encodes ABI-relevant scan indices and register semantics.

Risks and tests: changes affect all variants and can silently break scan layout, FIFO sizes, or PM logic. Test signals include all transport builds, channel scan-index validation, variant WHOAMI/default config selection, FIFO datum size calculations, and KABI-visible IIO sysfs behavior.
