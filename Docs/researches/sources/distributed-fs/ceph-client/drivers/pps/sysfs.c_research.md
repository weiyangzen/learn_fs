# sources/distributed-fs/ceph-client/drivers/pps/sysfs.c

Purpose: sysfs attributes for PPS source devices.

Important APIs/functions: `assert_show()`, `clear_show()`, `mode_show()`, `echo_show()`, `name_show()`, `path_show()`, `pps_attrs[]`, `pps_group`, and exported `pps_groups`.

Control flow: class registration in `pps.c` attaches `pps_groups` to every PPS device. Attribute reads print current assert/clear timestamp plus sequence when supported, static capability mode, whether echo callback exists, source name, and source path.

State/dependencies: reads per-device state from drvdata without taking `pps->lock`, so values can update concurrently with `pps_event()`. Depends on PPS core storing source info and timestamps.

Risks: uses `sprintf()` rather than `sysfs_emit()`; lockless reads can observe mixed timestamp/sequence pairs; unsupported assert/clear modes return an empty read rather than an error.

Test signals: read sysfs attributes before and after events, unsupported clear/assert mode behavior, concurrent PPS events during reads, name/path propagation from each client, and device removal while sysfs is open.
