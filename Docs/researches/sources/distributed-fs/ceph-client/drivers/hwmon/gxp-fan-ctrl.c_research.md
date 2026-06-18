# sources/distributed-fs/ceph-client/drivers/hwmon/gxp-fan-ctrl.c

## Purpose
`gxp-fan-ctrl.c` is a platform hwmon driver for HPE GXP fan controllers. It exposes eight fan fault/enable channels and eight writable PWM channels backed by memory-mapped controller registers.

## Important APIs, Types, and Functions
`struct gxp_fan_ctrl_drvdata` stores three MMIO bases: PWM base, platform register block (`plreg`), and function/status block (`fn2`). `fan_installed()`, `fan_failed()`, and `fan_enabled()` derive fan status from install/fail bits and the platform power bit. `gxp_pwm_read()` and `gxp_pwm_write()` implement PWM access. `gxp_fan_ctrl_read()`, `gxp_fan_ctrl_write()`, and `gxp_fan_ctrl_is_visible()` form the hwmon ops. `gxp_fan_ctrl_info` declares fixed fan and PWM channel counts.

## Control Flow
Probe allocates state, maps the unnamed base resource plus named `pl` and `fn2` resources, and registers `hpe_gxp_fan_ctrl` with `devm_hwmon_device_register_with_info()`. Reads of fan attributes consult installation/failure bits. Reads of PWM first check the power status register; when the platform power bit is clear, PWM reports zero to avoid stale/invalid hardware values. Writes validate `0..255` and write one byte at `base + channel`.

## State and Persistence
There is no software cache. PWM writes directly modify controller registers and persist according to hardware behavior. Fan enable/fault state is always read live from MMIO.

## Dependencies and Integration Points
The driver depends on platform resources described by device tree compatible `hpe,gxp-fan-ctrl`, MMIO accessors, and the hwmon callback API.

## Risks
Channel count is fixed at eight, so hardware variants with fewer registers depend on resource sizing and firmware correctness. PWM writes do not check fan installation or power state, while reads do, so user-observed state can differ after writes to absent/off fans. There is no locking, which is acceptable for simple MMIO bytes but means concurrent writes are last-writer-wins.

## Test Signals
Test resource mapping failures, all eight channel attributes, PWM range validation, power-off read returning zero, installed-bit gating, fault-bit reporting, and writes reaching the expected byte offsets.
