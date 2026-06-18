# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime.h

Purpose: shared helpers for proc uptime tests, converting both `/proc/uptime` and `CLOCK_BOOTTIME` into centiseconds for direct comparison.

Important APIs and functions: `clock_boottime()` wraps `clock_gettime(CLOCK_BOOTTIME)`. `proc_uptime()` uses `pread(fd, ..., 0)` and `xstrtoull()` from `proc.h` to parse the first uptime field as seconds plus two decimal digits.

Control flow: helpers assert successful reads and strict expected formatting `seconds.xx idle...`; only the first field is converted.

State and persistence: stateless inline-style helper definitions included by C files.

Dependencies and integration: includes `proc.h`, `<time.h>`, and standard assertions. It assumes `/proc/uptime` always exposes two decimal digits.

Risks and test signals: exact parsing ignores locale and wider fractional precision. Any format change trips assertions in consumers.
