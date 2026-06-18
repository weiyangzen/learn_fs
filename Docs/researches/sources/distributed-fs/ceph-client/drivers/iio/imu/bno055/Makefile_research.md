## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/Makefile

Purpose: build rules for BNO055 common, serial, serial trace, and I2C objects.

Important APIs, types, and functions: `obj-$(CONFIG_BOSCH_BNO055) += bno055.o` builds the shared core. `obj-$(CONFIG_BOSCH_BNO055_SERIAL) += bno055_ser.o` composes `bno055_ser-y := bno055_ser_core.o` and adds `bno055_ser_trace.o` when `CONFIG_TRACING` is enabled. `CFLAGS_bno055_ser_trace.o := -I$(src)` lets `define_trace.h` locate the local trace header. `obj-$(CONFIG_BOSCH_BNO055_I2C) += bno055_i2c.o` builds the I2C wrapper.

Control flow: object inclusion follows Kconfig symbols; tracepoint compilation is conditional on tracing.

State and persistence behavior: no runtime state; affects module composition.

Dependencies and integration points: integrates Linux tracepoint build requirements with the serdev transport and ensures common core is linked separately from bus wrappers.

Risks and edge cases: missing the `-I$(src)` flag would break tracepoint generation because `TRACE_INCLUDE_PATH` is local. The serial module's trace object is optional, so code must compile both with and without `CONFIG_TRACING`.

Test signals: compile serial with `CONFIG_TRACING=y` and `n`, compile I2C-only, and verify module object names and symbol namespace imports resolve.
