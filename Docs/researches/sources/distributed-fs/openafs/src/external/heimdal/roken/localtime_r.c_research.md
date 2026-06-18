# sources/distributed-fs/openafs/src/external/heimdal/roken/localtime_r.c

Purpose: fallback `localtime_r()` implementation.

Important APIs/types/functions: `localtime_r(const time_t *timer, struct tm *result)` under `#ifndef HAVE_LOCALTIME_R`.

Control flow: MSVC builds call `localtime_s(result, timer)` and return `result` on success. Other fallback builds call `localtime()`, copy the returned `struct tm` into caller storage, and return the caller buffer.

State and persistence behavior: writes into caller-provided `struct tm`. Non-MSVC path reads from libc static `localtime()` storage before copying.

Dependencies and integration points: portability shim for code requiring reentrant local time conversion.

Risks: non-MSVC fallback is not truly thread-safe because `localtime()` uses shared static storage. It only narrows the window by copying immediately. No null pointer checks.

Test signals: successful conversion, NULL/error propagation if libc returns NULL, and threaded stress on platforms using the fallback.
