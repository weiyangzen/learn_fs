# sources/compression/lz4/programs/util.c

Purpose: implements platform-specific CPU core counting for default worker selection.

Important APIs/functions: `UTIL_countCores()` uses `GetSystemInfo`, Apple `sysctlbyname`, Linux/POSIX `sysconf`, FreeBSD sysctls, or fallback `1`.

Control flow: per-platform branches cache detected counts and fall back to one when ordinary queries fail; unexpected FreeBSD sysctl errors can exit after `perror`.

State and persistence: static cached core count per process; no filesystem effects.

Dependencies/integration: includes `util.h`; used by `LZ4IO_defaultNbWorkers()` in `lz4io.c`.

Risks: topology detection is approximate and stale after CPU hotplug; fallback can underutilize; some FreeBSD errors terminate.

Test signals: indirectly covered by worker-default initialization and threaded CLI runs.
