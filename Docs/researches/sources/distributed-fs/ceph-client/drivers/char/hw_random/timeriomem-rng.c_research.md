# sources/distributed-fs/ceph-client/drivers/char/hw_random/timeriomem-rng.c

Purpose: generic hwrng driver for platforms where a fixed MMIO address yields a new 32-bit random value after a known period.

Important APIs, types, and functions: `struct timeriomem_rng_private`, `timeriomem_rng_read()`, `timeriomem_rng_trigger()`, `timeriomem_rng_probe()`, and remove.

Control flow: probe maps a 32-bit aligned resource, obtains period/quality from DT or platform data, initializes a completion and hrtimer, marks initial data present, and registers hwrng. Reads return 0 for non-waiting calls before the timer fires; blocking reads wait for completion, read one or more 32-bit words with period-based sleeps between additional words, then rearm the hrtimer.

State and persistence: per-device state tracks MMIO base, period, `present` flag, hrtimer, completion, and hwrng ops. Remove cancels the timer.

Dependencies and integration: platform data or OF properties, hrtimer/completion, MMIO, hwrng, and resource validation.

Risks and test signals: `present` is not protected by a lock, relying on hwrng serialization; period zero or very small periods could produce tight waits. Tests should cover missing period, bad resource alignment/size, nonblocking readiness, timer completion, multiword blocking reads, and remove during timer activity.
