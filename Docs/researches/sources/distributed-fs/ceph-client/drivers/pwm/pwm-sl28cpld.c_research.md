# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sl28cpld.c

## Purpose

`pwm-sl28cpld.c` exposes one PWM inside the Kontron sl28 CPLD. A 32 kHz 8-bit counter has four reset/prescaler modes, trading frequency for duty resolution.

## APIs, control flow, and state

`struct sl28cpld_pwm` stores parent regmap and offset. `get_state()` reads control/cycle, extracts enable and prescaler, computes period/duty, and clamps invalid combinations. `apply()` rejects inverted polarity, selects prescaler, computes cycle, remaps the prescaler-0 100% limitation to prescaler 1, and orders cycle/control writes depending on whether period is decreasing.

No software shadow exists; CPLD registers are read directly.

## Dependencies and integration points

The driver requires a parent regmap, a `reg` property for offset, compatible `kontron,sl28cpld-pwm`, and the PWM core.

## Risks and test signals

Prescaler and duty writes are not atomic and can glitch or leave inconsistent state after failures. 100% duty changes nominal frequency. Test all prescalers, write ordering, invalid initial registers, regmap errors, and disabled behavior.
