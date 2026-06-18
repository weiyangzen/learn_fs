# sources/distributed-fs/ceph-client/drivers/video/backlight/ktd253-backlight.c

## Purpose
This GPIO pulse-count modulation driver controls Kinetic KTD253/KTD259 backlight chips. The chip powers up at maximum current and each pulse steps brightness down through 32 ratios.

## Important APIs, Types, and Functions
`struct ktd253_backlight` stores device, backlight, GPIO, and current ratio. `ktd253_backlight_set_max_ratio()` drives GPIO high to establish max brightness. `ktd253_backlight_stepdown()` sends a precise low/high pulse using non-sleeping GPIO APIs and returns `-EAGAIN` if the low interval exceeded the critical off threshold. `ktd253_backlight_update_status()` computes target ratio, powers off on zero, resets to max if needed, and steps down until the target is reached.

## Control Flow
Probe reads and clamps `max-brightness` and `default-brightness`, gets the `enable` GPIO, holds it low long enough to force off, registers a backlight, initializes core brightness/power fields, and applies status. Runtime updates either power the chip off or loop through timing-sensitive pulses. If a pulse was interrupted long enough to risk losing state, the driver powers off, re-enables max, and retries.

## State and Persistence
The software ratio cache is essential because the chip only supports relative step-down pulses. On power-off the cache becomes zero; on power-on the known state is max ratio. There is no nonvolatile storage.

## Dependencies and Integration Points
The driver depends on GPIO descriptors that can be used from non-sleeping context for pulse timing, device properties, delays, and the backlight core. It matches `kinetic,ktd253` and `kinetic,ktd259`.

## Risks
GPIO expanders or sleeping GPIO controllers are invalid despite descriptor APIs allowing them at probe. Interrupt latency can corrupt pulse timing; the driver detects only long low phases. The update loop may need many pulses when moving from low ratios to slightly higher ratios because the hardware wraps via max.

## Test Signals
Test property clamping, GPIO acquisition, initial off reset, zero brightness timing, stepping down from max to target, wrap from ratio 1 to 32, `-EAGAIN` recovery, and suspend/resume.
