# sources/distributed-fs/openafs/src/external/heimdal/roken/vsyslog.c

## Purpose
Provides a fallback `vsyslog` for platforms without one, including `%m` expansion using the saved `errno` value.

## Important APIs, Types, And Functions
The exported function is `vsyslog(int pri, const char *fmt, va_list ap)`. Private `simple_vsyslog` logs the raw format string if allocation fails.

## Control Flow
The function saves `errno`, copies and expands the format string by replacing `%m` with `strerror(saved_errno)`, allocates a formatted message with `vasprintf`, then calls `syslog(pri, "%s", buf)`. Any allocation failure falls back to logging the original format string literally.

## State And Persistence
No module state is retained. It writes to the system logger and uses transient heap buffers.

## Dependencies And Integration Points
`roken.h.in` maps `vsyslog` to `rk_vsyslog` when missing. It depends on roken `vasprintf`, libc `strerror`, and system `syslog`.

## Risks And Test Signals
The low-memory fallback intentionally discards variable arguments. `%m` expansion reallocates the format buffer and must preserve pointer offsets. Tests should cover `%m`, multiple `%m`, allocation-failure simulation if possible, normal format arguments, and syslog facility/priority preservation.
