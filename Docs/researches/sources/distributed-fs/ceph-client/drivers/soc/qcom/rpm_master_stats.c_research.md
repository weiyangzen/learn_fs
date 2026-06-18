# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpm_master_stats.c

## Purpose

`rpm_master_stats.c` exposes Qualcomm RPM Master Stats v2 records through debugfs. Each configured MSG RAM slice is mapped and displayed under `qcom_rpm_master_stats/<master-name>`.

## Important APIs, Types, and Functions

`struct rpm_master_stats` mirrors the packed firmware record: active cores, shutdown count, shutdown/bringup/wakeup timestamps, wakeup reason, transition durations, and XO shutdown counters. `struct master_stats_data` carries one mapped base and label. `master_stats_show()` copies a record from IO memory and prints fields. Probe parses `qcom,master-names` and matching `qcom,rpm-msg-ram` phandles.

## Control Flow

Probe counts master names, allocates data entries, creates the debugfs root, then for each index parses the MSG RAM phandle, maps resource 0 with `devm_ioremap()`, reads the matching label, and creates a debugfs file. Remove recursively removes the debugfs tree.

## State and Persistence Behavior

State is read-only debug mapping state. Stats are maintained by RPM firmware in MSG RAM and persist across debugfs reads. The driver has no writes and no file-backed persistence.

## Dependencies and Integration Points

It depends on OF phandles, `of_address_to_resource()`, debugfs, IO memory mapping, and platform driver binding to `qcom,rpm-master-stats`. There is intentionally no module device table, so it is a manually loaded debugging module.

## Risks and Edge Cases

The driver treats debugfs creation failure as fatal because debugfs is its only purpose. It maps shared resources manually rather than using platform helpers. Count mismatches between `qcom,master-names` and phandles fail at the first missing phandle. The packed layout must match firmware exactly.

## Test Signals

Test zero/missing master names, missing MSG RAM phandles, mapping failure, debugfs creation failure, multiple masters, field readout consistency, remove cleanup, and module autoload expectations given the intentional lack of `MODULE_DEVICE_TABLE`.
