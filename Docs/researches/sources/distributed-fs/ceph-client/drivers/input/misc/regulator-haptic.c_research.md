# sources/distributed-fs/ceph-client/drivers/input/misc/regulator-haptic.c

## Purpose
`regulator-haptic.c` presents a voltage-controlled regulator as a force-feedback rumble device. Rumble magnitude is mapped linearly between configured minimum and maximum microvolts, and nonzero magnitude enables the regulator.

## Important APIs, Types, and Functions
`struct regulator_haptic` stores device/input/regulator pointers, work item, mutex, active/suspended flags, voltage bounds, and current magnitude. `regulator_haptic_set_voltage()` maps 16-bit magnitude to voltage and toggles the regulator. `regulator_haptic_play_effect()` stores strong or weak rumble magnitude. `regulator_haptic_parse_dt()` reads `min-microvolt` and `max-microvolt`. Probe creates an exclusive `haptic` regulator-backed memless FF input device.

## Control Flow
Probe obtains platform data or DT voltage bounds, gets the `haptic` regulator exclusively, registers an `FF_RUMBLE` memless input device, and stores state. Playback records the selected magnitude and schedules work. Work runs under `haptic->mutex` and applies voltage unless suspended. Close cancels work and sets magnitude zero in hardware. Suspend obtains the mutex interruptibly, sets voltage zero, and marks suspended; resume clears suspended and reapplies any nonzero magnitude.

## State and Persistence Behavior
`magnitude`, `active`, and `suspended` are persistent driver state. The regulator voltage/enable state persists in hardware until the next work, close, suspend, or removal. The exclusive regulator handle prevents other consumers from changing the same supply while active.

## Dependencies and Integration Points
The driver depends on regulator consumer APIs, platform data or OF properties, input force-feedback core, workqueues, and PM ops. It integrates with userspace as `regulator-haptic` `FF_RUMBLE`.

## Risks and Edge Cases
There is no validation that `max_volt >= min_volt`; a bad platform/DT config can underflow the voltage range calculation. `regulator_haptic_close()` calls `regulator_haptic_set_voltage()` without taking the mutex, so it can race with suspend/resume work. `regulator_set_voltage()` is called even for zero magnitude before disabling, which may set the regulator to minimum voltage briefly. Suspend can return `-EINTR`, leaving device state unchanged.

## Test Signals
Tests should cover DT and platform-data voltage bounds, strong/weak rumble scaling, zero stop, invalid voltage ordering, regulator enable/disable/set-voltage failures, suspend/resume races with playback, close while work is active, and regulator balance through repeated effects.
