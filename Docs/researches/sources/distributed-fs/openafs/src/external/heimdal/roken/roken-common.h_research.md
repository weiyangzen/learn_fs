# sources/distributed-fs/openafs/src/external/heimdal/roken/roken-common.h

## Purpose
Defines common roken portability constants, calling convention macros, process-execution status helpers, and declarations for utility functions shared by generated `roken.h` variants.

## Important APIs, Types, And Functions
The header defines `ROKEN_LIB_FUNCTION`, `ROKEN_LIB_CALL`, C++ linkage wrappers, fallback constants for sockets, syslog, paths, file descriptors, `PATH_MAX`, signals, `getaddrinfo` error codes, name-info flags, and shutdown constants. It declares `simple_exec*`, `wait_for_process*`, `pipe_execv`, `eread`, `ewrite`, socket helpers, timeval helpers, pid-file helpers, environment helpers, `rk_warnerr`, `rk_realloc`, string-pool helpers, data dump helpers, close-on-exec helpers, `ct_memcmp`, `rk_random_init`, and `rk_mkdir`.

## Control Flow
There is no executable control flow. The header controls compilation by filling gaps when system headers or libraries do not provide common interfaces.

## State And Persistence
The file itself stores no runtime state, but it declares APIs that manage process children, environment arrays, pid files under `_PATH_VARRUN`, sockets, time values, and heap-backed string pools.

## Dependencies And Integration Points
`roken.h.in` includes this header after platform headers and type definitions are established. OpenAFS uses the resulting roken interface to compile Heimdal-derived portability code consistently across Unix and Windows.

## Risks And Test Signals
Macro collisions are the main risk: fallback definitions for `min`, `max`, syslog constants, path constants, and function names can affect consumers. Test signals are broad compile coverage across Unix, MSVC, IPv6/no-IPv6, and missing-feature configure matrices, plus runtime smoke tests for declared helpers.
