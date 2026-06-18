# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_controls.c

## Purpose
Registers SMU-managed fan outputs as Windfarm controls for PowerMac systems. It supports RPM and PWM fan nodes under the SMU device tree and sends fan commands through SMU firmware.

## Important APIs, Types, And Functions
`struct smu_fan_control` embeds one `wf_control` and stores fan type, SMU register ID, cached value, and min/max. `smu_set_fan()` sends `SMU_CMD_FAN_COMMAND`, trying the newer command format first and falling back globally to the older bitmap format on failure. `smu_fan_set()`, `smu_fan_get()`, `smu_fan_min()`, and `smu_fan_max()` implement Windfarm control ops. `smu_fan_create()` translates OF `location` names to canonical Windfarm fan names.

## Control Flow
Module init requires `smu_present()`, finds the SMU node, scans `rpm-fans` or compatible `smu-rpm-fans`, then scans `pwm-fans`. Each recognized node with `location`, `min-value`, `max-value`, and `reg` becomes a registered control and is stored on `smu_fans`. Exit unregisters all controls.

## State, Dependencies, And Integration
State is the global `smu_fans` list plus the global fallback flag `smu_supports_new_fans_ops`. It depends on SMU command queue/completion, OF properties, Windfarm control APIs, and provider name stability. PM81, PM91, PM112, and PM121 consume these controls by names such as `cpu-fan`, `system-fan`, `hard-drive-fan`, `optical-drive-fan`, and `cpu-pump-0`.

## Risks And Test Signals
`smu_fan_get()` returns the cached target rather than reading hardware, so sysfs/debug consumers may not see firmware-side changes. The new-command fallback is global after the first failure. Location-name matching is manually curated and case-sensitive. Test signals include old/new SMU command fallback, min/max property absence, unrecognized fan locations, RPM versus PWM control type, command completion status, and exit unregister coverage.
