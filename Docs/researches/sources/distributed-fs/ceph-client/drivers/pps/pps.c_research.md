# sources/distributed-fs/ceph-client/drivers/pps/pps.c

Purpose: LinuxPPS character-device core implementing `/dev/ppsN`, RFC 2783 ioctls, polling, fasync, ID allocation, class registration, and cookie lookup.

Important APIs/functions: `pps_register_cdev()`, `pps_unregister_cdev()`, exported `pps_lookup_dev()`, `pps_cdev_ioctl()`, `pps_cdev_compat_ioctl()`, `pps_cdev_poll()`, `pps_cdev_pps_fetch()`, `pps_cdev_open()`, and `pps_cdev_release()`.

Control flow: subsystem init registers class `pps` and a dynamic major for up to `PPS_MAX_SOURCES`. Source registration allocates an idr minor, initializes device fields, registers `ppsN`, and takes a device reference for the idr. Open looks up by minor and takes a reference. `PPS_GETPARAMS`, `PPS_SETPARAMS`, `PPS_GETCAP`, `PPS_FETCH`, and `PPS_KC_BIND` implement userspace control. Fetch waits indefinitely or with a timeout until `last_ev` changes, then copies assert/clear sequence and timestamp state. Unregister clears `lookup_cookie`, destroys the device, removes the idr entry, and drops the idr reference.

State/dependencies: global `pps_idr` protected by `pps_idr_lock`, global major, class with `pps_groups`, per-device waitqueue/spinlock/fasync state managed in `kapi.c`.

Risks: `PPS_SETPARAMS` and kernel consumer bind require `CAP_SYS_TIME`; timeout conversion can truncate nanoseconds to ticks; compat fetch manually copies compat time layouts; `pps_lookup_dev()` uses RCU over idr without taking a reference and is documented for limited ldisc use; open devices can outlive unregister through device references.

Test signals: ioctl coverage including permission failures and bad modes, blocking and timed `PPS_FETCH`, poll readiness before/after fetch, compat ioctl on 32-bit userspace, fasync SIGIO, lookup-cookie user through tty ldisc, idr exhaustion, and unregister with active readers.
