# sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel.h

Purpose: public internal header connecting BMI088-family bus wrappers to the shared accelerometer core. It declares the chip type enum, shared regmap config, PM ops, and core probe/remove routines.

Important contract: `enum bmi_device_type` has `BOSCH_BMI085`, `BOSCH_BMI088`, `BOSCH_BMI090L`, and `BOSCH_UNKNOWN`; the bus wrappers pass these values from ID tables to the core. The exported functions accept a `struct device`, `struct regmap`, IRQ, and type. PM ops are exported so wrappers can bind the same runtime suspend/resume behavior.

Integration and risks: this header is the namespace boundary for `IIO_BMI088`. A mismatch between enum order and the core chip-info table would select wrong scale/name defaults, so ID table changes should be reviewed with the core table. Test signals include compilation of both wrappers, namespace imports, correct ID-to-type mapping, and PM op linkage.
