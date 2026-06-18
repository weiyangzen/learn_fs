# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_devfreq.c

`panthor_devfreq.c` implements Panthor DVFS through Linux devfreq, OPP tables, simple_ondemand governor data, optional thermal cooling registration, and scheduler-provided busy/idle accounting.

The private `struct panthor_devfreq` stores the devfreq handle, governor thresholds, busy and idle time accumulators, last update timestamp, last busy state, and spinlock. External APIs are `panthor_devfreq_init()`, `panthor_devfreq_resume()`, `panthor_devfreq_suspend()`, `panthor_devfreq_record_busy()`, `panthor_devfreq_record_idle()`, and `panthor_devfreq_get_freq()`. Devfreq callbacks are target, status, and current-frequency helpers.

Initialization handles existing power-domain OPP tables or installs DT OPP/regulator data, keeps optional SRAM enabled, sets the current recommended OPP, records the fastest OPP in `ptdev->fast_rate`, sets governor thresholds, registers devfreq, and attempts cooling-device registration. Busy/idle hooks fold elapsed time into the active accumulator under spinlock. The status callback reports current clock, busy time, total time, then resets accounting.

State persists in `ptdev->devfreq` and `ptdev->fast_rate`; OPP/regulator/devfreq resources are managed. Dependencies are clk, OPP, regulators, devfreq, devfreq cooling, DRM managed allocation, and Panthor device state. Risks include tiny total-time arithmetic in debug output, platform-specific OPP ownership, regulator coupling assumptions, and inaccurate DVFS if busy/idle hooks are missed. Tests should cover load scaling, idle downscaling, suspend/resume, OPP deferral, fdinfo frequency, and thermal cooling registration.
