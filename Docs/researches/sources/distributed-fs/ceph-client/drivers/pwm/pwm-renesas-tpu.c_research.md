# sources/distributed-fs/ceph-client/drivers/pwm/pwm-renesas-tpu.c

## Purpose

`pwm-renesas-tpu.c` drives Renesas TPU channels in PWM mode. It exposes four channels, supports both logical polarities, and handles 0%/100% duty by forcing fixed inactive/active pin states instead of running the timer.

## APIs, control flow, and state

`struct tpu_device` stores the platform device, shared `TSTR` lock, MMIO, clock, and four `struct tpu_pwm_device` shadows. Each channel caches timer state, polarity, prescaler, period, and duty. `tpu_pwm_set_pin()` programs `TIOR`; `tpu_pwm_start_stop()` serializes shared timer start bits; `tpu_pwm_timer_start()` powers/clocks, stops, configures `TCR/TMDR/TIOR/TGRA/TGRB`, and starts; `tpu_pwm_config()` computes a 16-bit period using prescalers 1/4/16/64 and can do duty-only updates.

Apply disables before polarity changes, configures enabled states, starts inactive channels, and drives inactive on disable. Persistent state is partly hardware and partly the per-channel software cache because there is no `.get_state`.

## Dependencies and integration points

It binds Renesas TPU compatibles, uses MMIO, a clock, runtime PM, spinlocks for shared `TSTR`, and the PWM framework.

## Risks and test signals

`pm_runtime_get_sync()` results are not checked in the timer-start path, and disable ignores possible start errors. Fixed-level handling can make `enabled=true` not imply a running timer. Test all channels, polarity changes while enabled, 0%/100%, duty-only updates, clock/PM balancing, and concurrent shared-start updates.
