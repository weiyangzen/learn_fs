<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio-vibra.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/gpio-vibra.c

## Purpose
`gpio-vibra.c` is a simple GPIO/regulator-backed vibrator driver. It exposes a memless `FF_RUMBLE` input device and turns a regulator plus enable GPIO on when rumble magnitude is nonzero.

## Important APIs, Types, and Functions
`struct gpio_vibrator` stores input, enable GPIO, `vcc` regulator, work item, and `running`/`vcc_on` state. `gpio_vibrator_play_effect()` chooses strong magnitude or weak magnitude, converts nonzero to `running`, and schedules work. `gpio_vibrator_start()` enables the regulator if needed and asserts the GPIO. `gpio_vibrator_stop()` deasserts GPIO and disables the regulator if it was enabled.

## Control Flow
Probe allocates state, input, regulator `vcc`, and `enable` GPIO, initializes work, configures `gpio-vibrator` with `FF_RUMBLE`, creates a memless FF handler, registers input, and stores platform data. Work starts or stops hardware based on `running`. Close cancels work, stops hardware, and clears `running`. Suspend cancels work and stops hardware if logically running; resume restarts if it was running.

## State and Persistence Behavior
`running` records the logical desired vibration across suspend/resume, while `vcc_on` prevents unbalanced regulator calls. No persistent storage exists.

## Dependencies and Integration Points
The driver uses platform devices, OF compatible `gpio-vibrator`, input FF memless, gpiod, regulator consumer APIs, and PM sleep callbacks.

## Risks and Test Signals
Risks include races around `running` and `vcc_on`, regulator enable failure leaving requested state true but hardware off, and no duration/magnitude scaling. Tests should cover strong/weak/zero playback, regulator failure on start, repeated starts/stops, close idempotence, and suspend/resume preserving logical running state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio-vibra.c -->
