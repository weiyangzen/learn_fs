# sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-hrtimer.c

Purpose: Software IIO trigger type that uses a high-resolution timer to poll attached IIO devices periodically at a configurable sampling frequency.

Important APIs/types/functions: `struct iio_hrtimer_info` embeds `iio_sw_trigger`, `hrtimer`, sampling-frequency pair, and period. Key functions are sampling-frequency show/store callbacks, `iio_hrtimer_trig_handler()`, `iio_trig_hrtimer_set_state()`, `iio_trig_hrtimer_probe()`, and remove.

Control flow: creating a software trigger allocates an IIO trigger, attaches sysfs attributes, initializes a monotonic hrtimer, sets default 100 Hz, registers it, and exposes it through configfs sw-trigger infrastructure. Enabling starts the hrtimer in hard relative mode; each expiry forwards the timer and calls `iio_trigger_poll()`. Disabling cancels the timer.

State and persistence: sampling frequency and period are in-memory trigger state. No persistence outside configfs-created trigger lifetime.

Dependencies/integration: depends on IIO software trigger framework, hrtimer, configfs item type, and IIO formatting/parsing helpers.

Risks: very high frequencies can create heavy interrupt context load. Store path updates frequency/period without explicit locking against an active timer. Fraction parsing uses centi-style multiplier then converts to mHz/uHz, so unit mistakes can affect ABI.

Test signals: create hrtimer trigger via configfs, read/write `sampling_frequency`, attach a buffered IIO device, verify poll cadence, and remove while active to ensure timer cancellation.
