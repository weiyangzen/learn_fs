# sources/distributed-fs/ceph-client/drivers/input/misc/pwm-beeper.c

## Purpose
`pwm-beeper.c` exposes a PWM-driven beeper as an input sound device. It maps `SND_BELL` and `SND_TONE` input events to PWM frequency and optional amplifier regulator control.

## Important APIs, Types, and Functions
`struct pwm_beeper` stores the input device, PWM, amplifier regulator, work item, requested period, bell frequency, suspend flag, and amplifier state. `pwm_beeper_on()` applies a 50 percent duty PWM state and enables the amplifier. `pwm_beeper_off()` disables amplifier then PWM. `pwm_beeper_event()` converts sound events to a nanosecond PWM period. `pwm_beeper_work()` applies the requested state. `pwm_beeper_suspend()` and `pwm_beeper_resume()` coordinate event locking with worker scheduling.

## Control Flow
Probe obtains the PWM, initializes it disabled, obtains the `amp` regulator, reads optional `beeper-hz` with a default of 1000 Hz, registers an input device with `EV_SND/SND_TONE/SND_BELL`, and stores driver data. Event callbacks reject non-sound or negative values, translate bell to configured frequency, write `beeper->period`, and schedule work unless suspended. The worker turns the PWM/regulator on for nonzero period and turns both off for zero. Close and suspend cancel work and force hardware off; resume clears the suspend flag and lets the worker restore any nonzero requested period.

## State and Persistence Behavior
The requested period is the persistent software intent across suspend/resume. `amplifier_on` tracks whether the regulator is enabled to avoid unbalanced regulator calls. Hardware PWM and regulator states persist until changed by the worker, close, suspend, or driver removal.

## Dependencies and Integration Points
The driver depends on platform/OF enumeration, `pwm-beeper` compatible, PWM core, regulator consumer API, input sound events, and device property `beeper-hz`. It integrates with userspace through evdev sound ioctls/events and with board hardware through the PWM and `amp` supply.

## Risks and Edge Cases
`HZ_TO_NANOSECONDS(value)` divides by the requested frequency; negative values are rejected but extremely large values can produce a zero or impractically small period. The period field is written without a dedicated mutex, relying on input event locking plus `READ_ONCE()` in the worker. Regulator enable failure disables the PWM but leaves the requested period intact, so later work may retry. Suspend uses the input `event_lock` specifically to avoid resubmitting work while setting `suspended`.

## Test Signals
Test `SND_BELL`, `SND_TONE`, zero stop events, invalid event types/codes, regulator failure paths, PWM apply failures, suspend/resume with an active tone, close while work is pending, and DT/property configurations with and without `beeper-hz`.
