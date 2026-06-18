# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_i2c.h

Purpose: declares Loongson GPIO-backed I2C state and creation helper.

Important APIs/types/functions: `struct lsdc_i2c` with adapter, bit-algo data, DRM device pointer, GPIO direction/data register pointers, and SDA/SCL masks; `lsdc_create_i2c_chan`.

Control flow: core modeset init calls creation per display pipe before connector creation.

State and persistence: per-pipe I2C adapter state persists for DRM device lifetime.

Dependencies and integration points: depends on Linux I2C and i2c-algo-bit. Used by output init for DDC.

Risks and test signals: adapter lifetime must match DRM device and display pipe. Test I2C bus registration/removal and EDID probing.
