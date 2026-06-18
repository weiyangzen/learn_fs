# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012-priv.h

Purpose: private state header for FC0012. It defines `struct fc0012_priv` containing the I2C adapter, immutable public config pointer, and cached frequency/bandwidth values.

There is no control flow. The implementation allocates this object in `fc0012_attach`, uses `cfg->i2c_address`, `xtal_freq`, `dual_master`, `loop_through`, and `clock_out` for initialization/tuning, and returns cached fields through DVB getter ops.

Dependencies are the public `fc0012_config` definition included before this header. Risks: the private struct stores a borrowed config pointer, so the parent-owned config must outlive the tuner; stale cached frequency/bandwidth can result if tuning fails before cache update. Test signals: attach with stack/static config lifetime review, release cleanup, and getter behavior before first successful tune.
