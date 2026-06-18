## sources/distributed-fs/moosefs/mfsmaster/missinglog.h

Purpose: declares the missing chunk log API for insertion, window rotation, serialization, and initialization.

Important APIs: `missing_log_insert` records a missing chunk reference; `missing_log_swap` rotates active entries into the reportable previous window; `missing_log_getdata` returns size or writes packed records depending on whether the buffer is NULL; `missing_log_init` initializes tables and reload handling.

Control flow and integration: chunk/filesystem code inserts events, a periodic task is expected to swap windows, and status code reads the previous window for client responses.

State and persistence behavior: implementation state is volatile and bounded by `MISSING_LOG_CAPACITY`; the header exposes no persistence controls.

Dependencies: only fixed-width integer types.

Risks: callers must pass nonzero chunk ids and correctly size buffers using the NULL-buffer size query before serialization. Mode controls record width, so client/server protocol must agree.

Test signals: compile coverage and serialization-size agreement tests for mode 0 and mode 1.
