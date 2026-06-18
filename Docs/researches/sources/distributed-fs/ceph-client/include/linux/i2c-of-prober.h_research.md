# sources/distributed-fs/ceph-client/include/linux/i2c-of-prober.h

## Purpose
Defines an OF dynamic component prober for discovering I2C-attached components that need temporary resources enabled before normal driver probing.

## APIs, Control Flow, and State
`struct i2c_of_probe_ops` supplies optional ordered callbacks: `enable()` powers or prepares components, `cleanup_early()` releases exclusive resources before probing a found component, and `cleanup()` balances enable on exit. `struct i2c_of_probe_cfg` binds ops to a device-node prefix type. With `CONFIG_OF_DYNAMIC`, `i2c_of_probe_component()` performs the probing. Simple helpers support one regulator and optional GPIO, with `struct i2c_of_probe_simple_opts` describing supply, GPIO polarity, and delays, and `struct i2c_of_probe_simple_ctx` storing regulator/GPIO handles.

## Dependencies, Integration, Risks, and Tests
Depends on kconfig, OF dynamic nodes, devices, regulators, GPIO descriptors, and sleeps. Integrates with display/touchpad/touchscreen-style components that are board-described but require power sequencing to respond on I2C. Risks include using devres from callbacks despite the warning, leaking resources when `cleanup_early()` already released them, misspelled documentation reference `free_resourcs_late`, delay/polarity mistakes, and missing `-EPROBE_DEFER` handling. Test signals include OF dynamic probe success/failure paths, regulator/GPIO sequencing, no-component cleanup, component-found cleanup-early order, and !CONFIG_OF_DYNAMIC builds.
