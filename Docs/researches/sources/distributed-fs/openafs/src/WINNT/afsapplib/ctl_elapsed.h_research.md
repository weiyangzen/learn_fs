## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_elapsed.h

Purpose: Declares the elapsed-time custom control interface and helper macros for converting between `SYSTEMTIME` fields and seconds.

Important APIs and definitions: `RegisterElapsedClass`, constants `csec1SECOND` through `csec1WEEK`, `SET_ELAPSED_TIME`, `SET_ELAPSED_TIME_FROM_SECONDS`, `GET_SECONDS_FROM_ELAPSED_TIME`, messages `ELM_GETRANGE`, `ELM_SETRANGE`, `ELM_GETTIME`, `ELM_SETTIME`, notifications `ELN_CHANGE`/`ELN_UPDATE`, and `EL_*` macros.

Control flow: Header macros send `SYSTEMTIME*` payloads to controls. Conversion macros mutate their arguments directly and are intended for elapsed durations, not calendar times.

State and persistence: None in the header.

Dependencies and integration points: Consumers must use `SYSTEMTIME` as a duration structure, with `wDay` representing elapsed days and `wHour` the remainder. Used by the implementation and any dialogs embedding elapsed controls.

Risks: `SET_ELAPSED_TIME_FROM_SECONDS` mutates the `_s` argument, so callers passing expressions or reused variables can be surprised. Macros are multi-statement without `do { } while (0)`, making them unsafe in single-line conditional contexts.

Test signals: Conversion macro round trips, range/get/set message macros, and compile checks in conditional statements.
