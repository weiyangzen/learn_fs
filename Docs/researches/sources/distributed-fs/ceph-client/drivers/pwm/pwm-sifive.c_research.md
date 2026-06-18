# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sifive.c

## Purpose

`pwm-sifive.c` drives SiFive PWM IP with four compare outputs sharing one scaled counter period. The compare registers encode inactive time, so the driver inverts values to present a conventional active-high PWM API.

## APIs, control flow, and state

`struct pwm_sifive_ddata` stores device, lock, notifier, clock, MMIO, real/approximate periods, and user count. `pwm_sifive_update_clock()` programs `PWMCFG` scale and computes actual period. Apply rejects inverted polarity, computes inverted compare, prevents period changes by multiple users, updates scale under lock, enables clock if needed, writes `PWMCMP`, and disables clock for disabled states. A clock notifier recomputes period after rate changes.

`approx_period`, `real_period`, and `user_count` are key software state; active outputs own clock enables.

## Dependencies and integration points

It binds `sifive,pwm0`, uses MMIO, clock notifiers, a prepared clock with manual enables, and the PWM core.

## Risks and test signals

All outputs share period; conflicting users get `-EBUSY`. Period+duty changes can produce one mixed cycle. Hardware cannot generate true 0%. Probe reconstruction of enabled outputs from `PWMCMP > 0` should be validated. Test shared-period conflicts, notifier updates, duty inversion, boot-enabled refcounts, and remove-time clock balance.
