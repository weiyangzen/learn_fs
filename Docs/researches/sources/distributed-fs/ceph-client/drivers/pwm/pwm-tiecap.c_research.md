# sources/distributed-fs/ceph-client/drivers/pwm/pwm-tiecap.c

## Purpose

`pwm-tiecap.c` drives TI eCAP modules in APWM mode. One PWM output uses CAP1/CAP2 for inactive updates and CAP3/CAP4 shadow registers for live updates. On disable the pin becomes input.

## APIs, control flow, and state

`struct ecap_pwm_chip` stores clock rate, MMIO, and suspend context. `ecap_pwm_config()` computes cycles, resumes runtime PM, sets APWM/sync-disabled mode, writes active or shadow registers depending on current enable, and clears APWM for inactive configuration. Polarity toggles `APWM_POL_LOW`; enable sets free-run/APWM; disable clears both and releases PM. Suspend/resume save/restore CAP3/CAP4/ECCTL2.

Context storage is the only software persistence; no `.get_state` exists.

## Dependencies and integration points

It binds `ti,am3352-ecap` and legacy `ti,am33xx-ecap`, uses `fck`, MMIO, runtime PM, and PWM core.

## Risks and test signals

Several `pm_runtime_get_sync()` calls ignore errors. Disabled pin is input/floating. Periods >1s are rejected. Test polarity, shadow live update, suspend/resume, legacy clock, PM failure injection, and disable pin level.
