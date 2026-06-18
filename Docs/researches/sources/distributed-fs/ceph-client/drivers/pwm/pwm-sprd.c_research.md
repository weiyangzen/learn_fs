# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sprd.c

## Purpose

`pwm-sprd.c` supports Spreadtrum/Unisoc PWM blocks such as UMS512. It exposes up to four channels, each with enable and output clocks, fixed maximum modulus, and an 8-bit prescaler.

## APIs, control flow, and state

`sprd_pwm_clk_init()` discovers channel clock pairs (`enableN`, `pwmN`). `get_state()` enables clocks, reads enable/prescale/duty, reconstructs period and duty, and keeps clocks enabled if hardware is active. `sprd_pwm_config()` writes prescale, fixed `MOD`, and duty last because the duty write applies values. Apply enables clocks for inactive channels, configures, sets enable, or disables immediately and turns clocks off.

No software period/duty state exists; active hardware state drives clock references.

## Dependencies and integration points

The driver binds `sprd,ums512-pwm`, depends on named per-channel clocks, MMIO, and the PWM core.

## Risks and test signals

Long periods saturate prescale, disable is immediate, and missing clocks for an early channel stop discovery of later channels. Test clock discovery, duty-last latch behavior, boot-enabled get_state, prescale limits, polarity rejection, and clock balance.
