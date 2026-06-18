<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio-beeper.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/gpio-beeper.c

## Purpose
`gpio-beeper.c` is a generic platform driver that maps input sound events to a GPIO-controlled beeper. It exposes `EV_SND/SND_BELL` and toggles an output GPIO asynchronously.

## Important APIs, Types, and Functions
`struct gpio_beeper` stores a work item, GPIO descriptor, and desired `beeping` state. `gpio_beeper_event()` is the input event callback; it accepts only `EV_SND/SND_BELL`, rejects negative values, records the boolean state, and schedules work. `gpio_beeper_work()` applies the state through `gpiod_set_value_cansleep()`. `gpio_beeper_close()` cancels work and forces the GPIO off.

## Control Flow
Probe allocates state, obtains the unnamed GPIO as `GPIOD_OUT_LOW`, allocates a devm input device, initializes work, fills input IDs and callbacks, advertises `SND_BELL`, stores private data, and registers input. User-space sound events enter through evdev and are converted to workqueue GPIO writes.

## State and Persistence Behavior
`beeping` is the only software state and is not persistent. GPIO state is forced low on close and starts low at probe.

## Dependencies and Integration Points
The driver binds as `gpio-beeper` and OF compatible `gpio-beeper`, using gpiod consumers, input event callbacks, and workqueues.

## Risks and Test Signals
Risks include lack of locking around `beeping` versus scheduled work, unsupported sound codes returning `-ENOTSUPP`, and GPIO sleep requirements necessitating deferred work. Tests should cover event validation, positive/zero bell values, close cancellation, initial low output, and probe failure when GPIO or input allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio-beeper.c -->
