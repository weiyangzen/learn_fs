## sources/distributed-fs/openafs/src/vol/common.c

Purpose: small shared logging and fatal-exit helpers for volume package tools and library code.

Important APIs/types/functions: defines global `int Statistics`. `Log()` chooses ViceLog level `-1` when statistics mode is enabled and `0` otherwise, then delegates to `vViceLog`. `Abort()` logs a program-aborted prefix and formatted message, then calls `abort()`. `Quit()` logs a formatted message and exits with status `1`.

Control flow: all three functions are variadic wrappers around OpenAFS logging. `Abort()` and `Quit()` do not return.

State and persistence: only mutable state is the process-global `Statistics` flag. Persistence is limited to whatever `ViceLog` backend writes. `Abort()` may produce a core dump depending on platform/runtime settings.

Dependencies: OpenAFS config/param, roken, `afs/afsutil.h` for `ViceLog`/`vViceLog`, standard varargs, `abort`, and `exit`.

Integration points: included by volume sources such as `clone.c` and `daemon_com.c` for consistent diagnostics and fatal handling. Declarations live in `common.h`; object is included in `VLIBOBJS`.

Risks: fatal helpers terminate the process, so library callers must know these are not recoverable paths. The logging call style uses the OpenAFS double-parentheses convention and should be preserved. The global `Statistics` flag changes log level process-wide.

Test signals: unit or harness tests can stub `vViceLog`/`ViceLog` to verify level selection, format propagation, `Abort()` non-return behavior, and `Quit()` exit status.
