# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c.h

Purpose: declares the top-level DCE I2C helper functions and includes both hardware and software engine interfaces so callers can submit I2C commands without selecting the backend directly.

Important APIs: `dce_i2c_oem_device_present()` reports whether a BIOS-advertised OEM I2C device matches a slave address on a DDC service. `dce_i2c_submit_command()` submits a `struct i2c_command` against a `struct ddc`, internally choosing hardware I2C or software bit-banging.

Control flow and integration: this header is included by DDC/display code and by the backend implementations. It forms the small public façade over `dce_i2c_hw.c` and `dce_i2c_sw.c`.

State and persistence: no state is declared besides the function contracts. Backend state is in `struct dce_i2c_hw`, `struct dce_i2c_sw`, GPIO/DDC objects, and resource-pool flags.

Dependencies and risks: depends on `inc/core_types.h`, `dce_i2c_hw.h`, and `dce_i2c_sw.h`. The main maintenance risk is exposing backend structs through the façade include, which couples users to backend type definitions. Test signals are successful compilation of callers with both backends and runtime coverage of backend fallback.
