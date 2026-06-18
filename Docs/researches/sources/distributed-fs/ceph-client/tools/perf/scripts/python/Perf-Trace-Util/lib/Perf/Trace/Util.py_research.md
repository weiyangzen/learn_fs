<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Util.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Util.py
Purpose: Miscellaneous Python utilities for perf trace scripts: time conversion, running stats, terminal clearing, syscall name lookup, and errno formatting.

Important APIs/types/functions: Defines futex constants, `NSECS_PER_SEC`, `avg`, `nsecs`, `nsecs_secs`, `nsecs_nsecs`, `nsecs_str`, `add_stats`, `clear_term`, `syscall_name`, and `strerror`. Optional audit integration maps machine names to audit architecture ids.

Control flow: At import time it tries to import `audit`, chooses `machine_id` from `os.uname()[4]`, and prints one warning if audit is unavailable. `syscall_name` uses audit when possible and otherwise returns the numeric id as a string.

State and persistence: `audit_package_warned` and `machine_id` are module-level state. `add_stats` mutates a caller-provided dictionary. No persistence.

Dependencies and integration points: Used by Python perf scripts that need syscall names, errno names, or nanosecond formatting. Optional dependency on python-audit affects output quality.

Risks: Import-time warning can affect script output. `nsecs_str` creates a one-element tuple due to a trailing comma, which may be a latent formatting bug. `add_stats` uses a simple average update rather than a mathematically exact running average over all values.

Test signals: Scripts that format syscall counts or futex errors exercise audit/errno helpers; unit checks should cover `nsecs_str` and `add_stats` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Util.py -->
