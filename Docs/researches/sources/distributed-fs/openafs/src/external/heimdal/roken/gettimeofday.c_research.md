# sources/distributed-fs/openafs/src/external/heimdal/roken/gettimeofday.c

Purpose: fallback `gettimeofday()` implementation for platforms missing it.

Important APIs/types/functions: `gettimeofday(struct timeval *tp, void *ignore)` under `#ifndef HAVE_GETTIMEOFDAY`.

Control flow: on Windows, reads `FILETIME`, converts from Windows epoch 100ns units to Unix epoch microseconds, and fills `tv_sec`/`tv_usec`. On other fallback platforms, uses `time(NULL)` and sets microseconds to zero.

State and persistence behavior: read-only wall-clock query into caller-provided struct.

Dependencies and integration points: portability layer for code needing `struct timeval` timestamps.

Risks: non-Windows fallback has only one-second precision. No null pointer guard. Uses platform-specific integer suffixes in Windows code.

Test signals: Windows epoch conversion sanity, monotonic-ish wall-clock progression, microsecond range validation, and fallback non-Windows precision expectations.
