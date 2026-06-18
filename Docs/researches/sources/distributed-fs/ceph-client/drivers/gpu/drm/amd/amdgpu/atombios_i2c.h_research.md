# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_i2c.h

Purpose: declares the AtomBIOS-backed I2C transfer interface for AMDGPU.

Important APIs: `amdgpu_atombios_i2c_xfer()` is the adapter transfer callback; `amdgpu_atombios_i2c_func()` returns I2C capability flags; `amdgpu_atombios_i2c_channel_trans()` exposes a direct one-byte transaction helper over a selected AtomBIOS line.

Control flow: no implementation is present, but the declarations are used by AMDGPU I2C adapter setup and low-level display/firmware helpers that need AtomBIOS I2C transactions.

State and persistence: the header is stateless. Declared functions operate on `struct i2c_adapter`, `struct i2c_msg`, and `struct amdgpu_device` state and affect hardware I2C transactions.

Dependencies and integration points: relies on Linux I2C types and AMDGPU device types being visible to includers. It connects AMDGPU display probing code with the implementation in `atombios_i2c.c`.

Risks: prototype drift would break adapter registration. The direct helper signature uses raw byte arguments, making address/offset interpretation a caller responsibility.

Test signals: build users of AtomBIOS I2C adapter setup; runtime EDID/DDC reads verify the declared transfer path.
