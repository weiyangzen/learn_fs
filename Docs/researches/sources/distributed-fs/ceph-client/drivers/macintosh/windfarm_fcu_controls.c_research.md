# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_fcu_controls.c

## Purpose
Implements Windfarm fan controls for PowerMac FCU I2C fan controllers. It discovers fan and pump channels from device tree, maps Apple location names to Windfarm control names, exposes RPM and PWM controls, and derives min/max limits from MPU EEPROM data or conservative defaults.

## Important APIs, Types, And Functions
`struct wf_fcu_priv` stores the I2C client, lock, fan list, kref, and RPM shift. `struct wf_fcu_fan` wraps one `wf_control`. Low-level I2C helpers are `wf_fcu_read_reg()` and `wf_fcu_write_reg()`. RPM ops are `wf_fcu_fan_set_rpm()` and `wf_fcu_fan_get_rpm()`; PWM ops are `wf_fcu_fan_set_pwm()` and `wf_fcu_fan_get_pwm()`. Discovery is handled by `wf_fcu_lookup_fans()`, `wf_fcu_default_fans()`, `wf_fcu_add_fan()`, and `wf_fcu_init_chip()`.

## Control Flow
Probe allocates controller state, initializes FCU active masks and the RPM shift, scans child nodes for `fan-rpm-control`, `fan-rpm`, `fan-pwm-control`, or `fan-pwm`, and registers controls. If device-tree discovery fails on PowerMac7,2, a hardcoded fan list is used. Set operations clamp requested values to `fan->min` and `fan->max`, encode RPM or PWM register values, and write the FCU. Get operations check failure and active bitmaps before reading programmed RPM or PWM state.

## State, Dependencies, And Integration
State is per I2C FCU and per registered fan. The private kref keeps controller state alive while controls exist. It depends on I2C master transfers, OF child properties (`location`, `reg`, node type), Windfarm control APIs, and `wf_get_mpu()` for CPU fan and pump limits. PM72 and RM31 model drivers consume the generated controls by stable names such as `cpu-front-fan-0`, `cpu-pump-0`, and `slots-fan`.

## Risks And Test Signals
I2C retry behavior is asymmetric and write operations are not protected by `pv->lock`, unlike reads. Device-tree name translation is fragile and missed names leave models without required controls. Pump min/max EEPROM data is known unreliable and falls back only after sanity checks. Test signals include FCU register read/write errors, inactive/failure bit handling, PowerMac7,2 fallback fan creation, RPM shift detection, duplicate names, and control-loop response to `-EFAULT` fan failures.
