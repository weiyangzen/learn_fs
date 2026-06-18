# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.c

Purpose: Linux I2C adapter implementation for the SMU v11 SMUIO DesignWare-style I2C controller, primarily for RAS/FRU EEPROM access shared with firmware.

Important APIs, types, and functions: exported `smu_v11_0_i2c_control_init()` registers the adapter and `smu_v11_0_i2c_control_fini()` clears bus pointers. Static helpers manage clock gating, enable/disable, status clearing, controller configuration, clock timing, target address, TX/RX polling, transmit/receive, abort, activity detection, bus lock/unlock, I2C transfer, and functionality reporting. The file defines custom error bits such as `I2C_SW_TIMEOUT`, `I2C_ABORT`, and restart flag `I2C_X_RESTART`.

Control flow: adapter transfers call `smu_v11_0_i2c_xfer()`, which initializes the controller, tracks address/direction changes to emit restart, marks the final message with STOP, dispatches reads or writes, then finalizes the controller. Lock ops serialize through `smu_i2c->mutex` and ask SMU firmware for bus ownership via `amdgpu_dpm_smu_i2c_bus_access()`. Init disables clock gating, aborts if activity is stuck, disables the IP, configures master fast-mode capability, and writes fixed timing values.

State and persistence: state is in SMUIO I2C registers, the `amdgpu_smu_i2c_bus` adapter/mutex/port fields, and `adev->pm` bus pointers and `bus_locked` flag. EEPROM contents are external to the driver; the driver itself stores no persistent data.

Dependencies and integration points: depends on Linux I2C core, amdgpu DPM/SMU arbitration, SMUIO v11 register headers, DRM logging, PCI device parentage, and HWMON-class adapter consumers.

Risks and test signals: fixed clock programming assumes a 100 MHz reference and effectively standard-speed timing despite fast-mode configuration. Clock gating is deliberately not restored because it can break later SMU bus use. `trylock_bus` always warns/fails, so atomic I2C users are unsupported. Test signals include EEPROM reads/writes, repeated-message restart/STOP behavior, timeout/NAK reporting, bus lock/unlock balance, and recovery after a stuck controller activity bit.
