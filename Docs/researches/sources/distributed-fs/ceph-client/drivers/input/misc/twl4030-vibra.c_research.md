# sources/distributed-fs/ceph-client/drivers/input/misc/twl4030-vibra.c

## Purpose
`twl4030-vibra.c` exposes the TWL4030 vibrator H-bridge as a memless force-feedback rumble device. It programs TWL audio/vibra registers, manages audio power/APLL resources, and disables LEDs that share the vibra PWM resource.

## Important APIs, Types, and Functions
`struct vibra_info` stores device/input, work item, enabled flag, speed, direction, and codec coexistence flag. `vibra_disable_leds()` clears LEDA/LEDB enable bits. `vibra_enable()` powers audio resource and H-bridge, then enables APLL. `vibra_disable()` powers down H-bridge and resources. `vibra_play_work()` applies speed/direction and `TWL4030_REG_VIBRA_SET`. `vibra_play()` maps FF magnitudes/direction to speed and direction.

## Control Flow
Probe requires the parent TWL4030 OF node, detects whether a codec child coexists, initializes work, creates a memless `FF_RUMBLE` input device, registers it, disables shared LEDs, and stores state. Playback stores speed from strong or weak magnitude and direction from effect direction, then schedules work. The worker checks whether audio routing owns vibra when coexistence is present, enables resources if needed, writes direction and PWM strength, or disables if speed is zero. Close and suspend cancel/disable active vibration; resume disables LEDs again.

## State and Persistence Behavior
`enabled`, `speed`, `direction`, and `coexist` persist in driver memory. TWL audio/vibra/LED registers persist in hardware. The driver intentionally disables LEDA/LEDB because they cannot coexist with vibra PWM.

## Dependencies and Integration Points
Depends on TWL MFD I2C helpers, TWL4030 audio resource APIs, input FF core, OF parent node, workqueues, and platform driver binding `twl4030-vibra`. It may coexist with TWL4030 codec/audio routing.

## Risks and Edge Cases
Most TWL I2C read/write return values are ignored, so hardware failures can desynchronize `enabled`. If codec coexistence indicates `TWL4030_VIBRA_SEL`, playback stops to avoid conflicting with audio. Strength mapping produces `256 - pwm`, with 1 as max and 255 as min per hardware comments. Explicit `input_ff_destroy()` on registration failure must stay consistent with input core ownership.

## Test Signals
Test rumble strength/direction mapping, coexistence with codec route, LED disable on probe/resume, suspend/close while active, TWL I2C failure injection, audio resource enable/disable balance, and repeated play/stop cycles.
