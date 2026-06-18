# sources/distributed-fs/ceph-client/drivers/input/misc/twl6040-vibra.c

## Purpose
`twl6040-vibra.c` controls the TWL6040 dual vibrator outputs as a memless force-feedback device. It handles left/right motor supplies, motor/driver resistance properties, overcurrent IRQs, errata sequencing, and amplitude code calculation.

## Important APIs, Types, and Functions
`struct vibra_info` stores device/input, work, IRQ, enabled flag, weak/strong speeds, direction, resistance values, two bulk regulators, and parent `struct twl6040`. `twl6040_vib_irq_handler()` handles overcurrent status. `twl6040_vibra_enable()` enables regulators, powers TWL6040, and enables vibra drivers with ES1.1 errata delay. `twl6040_vibra_code()` calculates VIBDAT codes from voltage/resistance/speed/direction. `twl6040_vibra_set_effect()` writes left/right VIBDAT registers. `vibra_play_work()` applies or disables effects.

## Control Flow
Probe locates the parent `vibra` OF child, reads resistance and optional supply voltage properties, requests the vibra IRQ, gets parent-device regulators `vddvibl` and `vddvibr`, optionally sets fixed regulator voltages, creates a memless `FF_RUMBLE` input device, and registers it. Playback stores weak/strong magnitudes and direction sign, then schedules work. The worker refuses to run when vibra routing is configured for audio, enables hardware if needed, writes amplitude codes, or disables when both strengths are zero. IRQ handling clears left/right vibra enable bits on overcurrent.

## State and Persistence Behavior
Driver state persists motor parameters, regulator handles, speeds, direction, enabled flag, and IRQ. Hardware state includes TWL6040 power, VIBCTL/VIBDAT registers, and regulator voltages/enables. Suspend and close cancel work and disable hardware if active.

## Dependencies and Integration Points
Depends on TWL6040 MFD APIs, regulator bulk APIs, OF properties under the parent `vibra` node, platform IRQs, input FF core, and workqueues. It integrates with TWL6040 audio/vibra routing through `twl6040_get_vibralr_status()`.

## Risks and Edge Cases
Resistance validation rejects only pairs where both driver and motor values are zero; a single zero can still cause divide-by-zero or unrealistic amplitude math. `regulator_get_voltage()` return values are not checked before division/scaling. Overcurrent handling disables registers but does not update `info->enabled`, so software may believe hardware is still active. Audio routing prevents effects but does not clear requested speeds.

## Test Signals
Test OF resistance/voltage parsing, divide-by-zero edge values, regulator enable/voltage failures, ES1.1 errata path, overcurrent IRQs for both channels, audio-route refusal, weak/strong/direction scaling, suspend/close cleanup, and repeated playback cycles.
