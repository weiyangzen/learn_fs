# sources/distributed-fs/ceph-client/drivers/s390/cio/css.c

## Purpose
This file implements the s390 Channel Subsystem bus (`css`), subchannel discovery/registration, CRW-driven slow-path evaluation, channel-subsystem sysfs attributes, a CSS-wide DMA pool, and CSS driver registration.

## Important APIs, Types, and Functions
Exports include `for_each_subchannel()`, `for_each_subchannel_staged()`, `css_alloc_subchannel()`, `css_register_subchannel()`, `css_sch_device_unregister()`, `get_subchannel_by_schid()`, `css_sch_is_valid()`, `css_sched_sch_todo()`, `css_schedule_eval()`, `css_schedule_eval_all()`, `css_schedule_eval_cond()`, `css_wait_for_slow_path()`, `css_schedule_reprobe()`, `css_complete_work()`, `sch_is_pseudo_sch()`, `css_driver_register()`, and `css_driver_unregister()`. It owns `css_init_done`, `max_ssid`, `channel_subsystems[]`, the `css_bus_type`, `slow_subchannel_set`, `cio_work_q`, and the CIO DMA gen_pool.

## Control Flow
`channel_subsystem_init()` initializes CHSC, detects CSS characteristics, enables multiple subchannel sets if possible, initializes slow-path state, registers CRW handlers and the CSS bus, creates the CSS device and pseudo subchannel, registers reboot cleanup, initializes DMA/airq/ISC state, registers the I/O subchannel driver, registers early console subchannels, and schedules full evaluation. Fast CRW handling calls `css_evaluate_subchannel(..., slow=0)`, which defers new/complex work with `-EAGAIN`. Slow-path work iterates staged known and unknown subchannels, probes new devices with `stsch()`/`css_probe_device()`, calls driver `sch_event()` for known subchannels, and tracks pending IDs in `slow_subchannel_set`. Sysfs `rescan` schedules and completes a full evaluation; `cm_enable` toggles CSS-wide channel measurement through CHSC.

## State and Persistence
State is in-memory bus/device state plus hardware subchannel status. Registered subchannels are Linux devices under the CSS bus. `slow_subchannel_set` records pending evaluations, `subchannel.todo` records per-subchannel work, and `channel_subsystem` stores channel paths, PGID, measurement buffers, and pseudo-subchannel. The DMA pool grows as needed and is freed only by explicit destroy paths. No disk persistence exists.

## Dependencies and Integration Points
It depends on CHSC initialization and characteristics, CRW source registration, low-level `stsch`, blacklist checks, CIO debug, idset helpers, Linux bus/device/workqueue APIs, reboot notifiers, DMA/genalloc, airq/ISC setup, and `device.c` for I/O subchannel handling. CSS drivers bind by subchannel type through `struct css_driver`.

## Risks and Test Signals
Risk areas include slow-path idset consistency, OOM fallback to brute-force scans, single-CSS assumptions, registration/unregistration races with workqueue references, subchannel validity rules for IO/MSG types, DMA pool growth and freeing, reboot-time CMF disable, and sysfs rescan blocking behavior. Test signals include full boot discovery, CRW-triggered add/remove/path-modification events, manual rescan, `cio_settle`, blacklisted device filtering, subchannel driver bind/unbind, pseudo-subchannel orphan movement, `cm_enable` toggling, DMA allocation/free users, and cleanup on init failure.
