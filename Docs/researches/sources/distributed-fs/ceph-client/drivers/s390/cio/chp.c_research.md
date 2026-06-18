# sources/distributed-fs/ceph-client/drivers/s390/cio/chp.c

## Purpose
This file manages registered s390 channel paths (`struct channel_path`) and their runtime/configuration state. It exposes channel-path sysfs attributes, registers channel paths discovered from SCLP/CRW/CHSC information, varies paths logically online/offline, and schedules SCLP configure/deconfigure operations.

## Important APIs, Types, and Functions
The main exported APIs are `chp_get_status()`, `chp_get_sch_opm()`, `chp_is_registered()`, `chp_update_desc()`, `chp_new()`, `chp_get_chp_desc()`, `chp_cfg_schedule()`, `chp_cfg_cancel_deconfigure()`, `chp_info_get_status()`, and `chp_ssd_get_mask()`. Internal state includes `chp_cfg_task[][]`, `cfg_lock`, `cfg_work`, `cfg_wait_queue`, cached `sclp_chp_info`, `info_lock`, and `chp_info_expires`. The sysfs surface includes `status`, `configure`, `type`, CMG/channel-measurement attributes, CHID/ESC/speed fields, and `util_string`.

## Control Flow
`chp_init()` registers the CRW handler for channel paths, initializes configure work, reads SCLP channel-path info, and registers initially configured or standby paths. `chp_new()` serializes on the CSS mutex, allocates a channel path, fetches CHSC descriptions/measurement characteristics, rejects invalid descriptors, registers the device, and attaches measurement attributes when channel measurement is enabled. Runtime `status` writes call `s390_vary_chpid()`, which updates logical state and calls `chsc_chp_vary()` to notify subchannels. `configure` writes enqueue `cfg_func()`, which issues `sclp_chp_configure()` or `sclp_chp_deconfigure()`, expires cached SCLP information, and propagates online/offline changes through CHSC helpers.

## State and Persistence
State is volatile kernel memory plus hardware/SCLP/CHSC channel-path state. `channel_subsystems[0]->chps[]` owns registered channel-path pointers. `chp_info` caches SCLP status for one jiffy and is refreshed on expiry or after configure changes. Pending configure tasks persist only in `chp_cfg_task[][]` until the work item consumes them. Measurement data comes from CSS CUB/ECUB memory and live CHSC descriptors, not from disk.

## Dependencies and Integration Points
This file depends on SCLP channel-path configuration APIs, CRW handlers, CHSC description/measurement helpers, the CSS device hierarchy, the CIO debug facility, and sysfs device attributes. It integrates with `chsc.c` for channel-path online/offline/vary propagation, with `css.c` for slow-path settling, and with subchannel drivers through CHSC/CSS callbacks.

## Risks and Test Signals
Risk areas include races among sysfs vary/configure, CRW path events, and slow-path subchannel evaluation; stale `chp_info` if SCLP refresh fails; incomplete rollback when sysfs measurement attributes fail after device registration; and path-mask mistakes in `chp_ssd_get_mask()` when full-link-address validity is partial. Test signals include channel-path CRW injection, `status` and `configure` sysfs transitions, SCLP configure failure handling, registration of standby paths at boot, measurement attribute creation/removal when `cm_enable` changes, and subchannel path masks after vary on/off.
