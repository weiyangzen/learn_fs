# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_devfreq.h

`panthor_devfreq.h` exposes the Panthor frequency-management API while keeping devfreq internals opaque.

It forward-declares `struct panthor_device` and `struct panthor_devfreq` and declares `panthor_devfreq_init()`, `panthor_devfreq_resume()`, `panthor_devfreq_suspend()`, `panthor_devfreq_record_busy()`, `panthor_devfreq_record_idle()`, and `panthor_devfreq_get_freq()`. It also forward-declares devfreq and thermal cooling types.

There is no runtime flow in the header. Device initialization calls init, PM paths call suspend/resume, scheduler or GPU activity code records busy/idle transitions, and fdinfo reads current frequency.

No state is owned here; implementation state lives in `ptdev->devfreq`, with max rate in `ptdev->fast_rate`. Dependencies are deliberately light so driver files can use the hooks without pulling devfreq internals. Risks are API misuse through unpaired busy/idle transitions or assuming devfreq always exists; the implementation tolerates absent devfreq by returning early. Test signals are build coverage of device/driver/scheduler users and runtime activity accounting around submitted jobs.
