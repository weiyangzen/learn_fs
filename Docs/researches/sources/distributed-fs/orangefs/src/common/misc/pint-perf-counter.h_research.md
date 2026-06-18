# sources/distributed-fs/orangefs/src/common/misc/pint-perf-counter.h

Purpose: Declares the OrangeFS performance counter/timer framework. It defines defaults, operation enums, option enums, key/sample/counter structures, server key tables, server counter globals, and public mutation/export functions.

Important APIs and types: `PINT_perf_key` binds display names, numeric keys, and flags such as `PINT_PERF_PRESERVE`. `PINT_perf_sample` stores a start time, interval, value array, and next link. `PINT_perf_counter` stores locking, key/type/count metadata, history settings, rollover state, state-machine callback, and sample list. Operations include add/sub/set/start/end and options include history size, key count, and update interval. Macros erase counting/timer calls when `__PVFS2_DISABLE_PERF_COUNTERS__` is defined.

Control flow and integration: Servers and clients initialize counters with key arrays, record counts/timers throughout request paths, periodically roll over samples, and retrieve data for management APIs. The header intentionally keeps key arrays extern so management enum ordering can be shared.

State and persistence behavior: Counter state is volatile process memory. The `PINT_PERF_PRESERVE` flag controls what survives rollovers. No persistent storage is defined.

Dependencies and risks: Depends on PVFS management enums, `gen-locks`, and state-machine types. The caller must size retrieval buffers from key count, history, and counter type. Test signals include disabled-counter builds, timer/counter type separation, and management output compatibility.
