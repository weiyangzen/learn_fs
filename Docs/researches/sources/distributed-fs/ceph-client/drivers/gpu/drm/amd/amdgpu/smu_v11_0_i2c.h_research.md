# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.h

Purpose: public declaration header for SMU v11 SMUIO I2C adapter setup.

Important APIs, types, and functions: forward-declares `struct amdgpu_device` and declares `smu_v11_0_i2c_control_init()` plus `smu_v11_0_i2c_control_fini()`.

Control flow: no runtime flow in the header. Callers initialize the adapter during device setup and clear it during teardown.

State and persistence: no header state; implementation mutates `adev->pm.smu_i2c`, RAS/FRU bus pointers, and hardware registers.

Dependencies and integration points: depends only on Linux types and amdgpu device ownership. It exposes the I2C bridge to SMU/DPM and RAS EEPROM code.

Risks and test signals: build linkage catches signature drift. Runtime signal is creation and teardown of the "AMDGPU SMU 0" I2C adapter.
