# sources/distributed-fs/ceph-client/tools/thermal/tmon/sysfs.c

## Purpose
`sysfs.c` is the Linux thermal sysfs backend for `tmon`. It probes `/sys/class/thermal`, records thermal zones, trip points, cooling devices, and zone-to-device bindings, then samples live temperatures and cooling-device states. It also provides the write path used by the controller and TUI to set `cooling_device*/cur_state`.

## Important APIs, Types, and Functions
The file owns global `struct tmon_platform_data ptdata`, the `trip_type_name[]` mapping, a fixed three-record `trec[]` thermal history ring, and `cur_thermal_record`. Public functions include `probe_thermal_sysfs()`, `update_thermal_data()`, `set_ctrl_state()`, `get_ctrl_state()`, `zone_instance_to_index()`, `sysfs_set_ulong()`, and `free_thermal_data()`. Internal helpers read sysfs files (`sysfs_get_ulong()`, `sysfs_get_string()`), parse instance numbers (`get_instance_id()`), map trip type strings, scan thermal zones and cooling devices, and collect binding data from thermal-zone `cdev*` symlinks.

## Control Flow
Startup calls `probe_thermal_sysfs()`, which scans `THERMAL_SYSFS`, counts zone/device instances while tracking maximum instance IDs, allocates `ptdata.tzi` and optional `ptdata.cdi`, then calls `scan_tzones()` and `scan_cdevs()`. `scan_tzones()` walks possible `thermal_zoneN` paths, reads each zone type, discovers valid `trip_point_*_temp` nodes below `MAX_TEMP_KC`, reads matching trip types, and records cooling-device symlink bindings and trip bindings. `update_thermal_data()` advances the circular thermal record, timestamps it, samples each zone temperature, refreshes each cooling device by re-reading type/max/current, and appends a row to `tmon_log` when logging is enabled.

## State and Persistence
State is mostly process-global and in-memory: `ptdata`, `trec`, `cur_thermal_record`, cooling-device flags, and trip/cdev binding bitmaps. Persistent external effects are writes to thermal sysfs `cur_state` through `sysfs_set_ulong()` and optional rows in `/var/tmp/tmon.log` managed by `tmon.c`. `set_ctrl_state()` scales a percentage-like controller output against each matching cooling device `max_state`, while `get_ctrl_state()` reads the first controlled device directly from sysfs.

## Dependencies and Integration Points
This file depends on the Linux thermal sysfs ABI, directory entry types, symlink targets like `../cooling_deviceN`, and fields declared in `tmon.h`. `tmon.c` calls the probe/update/control APIs; `tui.c` displays `ptdata` and calls the write helpers. The controller consumes `trec` temperature records.

## Risks and Edge Cases
Parsing uses `strtok()` destructively in `get_instance_id()`, so callers must not reuse the original string after parsing. Arrays are bounded by constants like `MAX_NR_TRIP`, `MAX_NR_CDEV`, and bitmap width assumptions; very large or sparse sysfs instance IDs could exceed practical display or bitmap expectations. `sysfs_get_ulong()` and `sysfs_set_ulong()` return success even when `fscanf()`/`fprintf()` fail after open, and many probe calls do not check read failures before using partially initialized fields. `nl->d_type == DT_LNK` can be unreliable on filesystems that do not fill `d_type`, though sysfs normally does. `set_ctrl_state()` silently disables display control if a matching device has `max_state < 10`.

## Test Signals
Useful tests require a system or fixture exposing thermal sysfs. Validate probe behavior with multiple zones, sparse instance IDs, missing cdevs, invalid trip temperatures, and cdev symlink bindings. Runtime tests should confirm that sampling updates `trec`, that logging emits zone/cdev columns, and that controlled devices receive scaled `cur_state` writes only when `no_control == 0` and `CDEV_FLAG_IN_CONTROL` is set.
