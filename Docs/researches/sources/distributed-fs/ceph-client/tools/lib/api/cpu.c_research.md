<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/cpu.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/cpu.c

## Purpose
`cpu.c` provides one libapi helper for discovering a CPU maximum frequency from sysfs. It is intended for tools that need a coarse CPU frequency value without open-coding sysfs mount discovery and parsing.

## Important APIs, types, and functions
`cpu__get_max_freq(unsigned long long *freq)` is the only exported function. It reads `devices/system/cpu/online` with `sysfs__read_int()` to obtain a CPU number, constructs `devices/system/cpu/cpu%d/cpufreq/cpuinfo_max_freq`, and reads the unsigned long long value with `sysfs__read_ull()`.

## Control flow
The function fails early if the online CPU sysfs read fails. Otherwise it formats the cpufreq entry for the parsed CPU and delegates the final read to the fs helper. It returns `0` on success or the negative/error return from the lower-level helper.

## State and persistence behavior
There is no local state. The function reads live sysfs state on each call. Any caching of the sysfs mountpoint happens in `fs.c`, not here.

## Dependencies and integration points
It depends on `cpu.h` for the prototype and `fs/fs.h` for `PATH_MAX`, `sysfs__read_int()`, and `sysfs__read_ull()`. It integrates with tools that link `libapi.a`.

## Risks and edge cases
`devices/system/cpu/online` can contain CPU ranges such as `0-7`, while `sysfs__read_int()` uses `atoi()`-style parsing and will return only the leading integer. This means the helper effectively samples CPU0 on common systems. Systems without cpufreq, with offline CPU0, or with policy-only cpufreq layouts will fail.

## Test signals
Unit or runtime tests should mock `SYSFS_PATH` and provide cpu online/cpufreq files. Real-system checks should compare the returned value with `/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq` and verify failure behavior when cpufreq is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/cpu.c -->
