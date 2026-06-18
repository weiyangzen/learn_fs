# sources/compression/lz4/tests/check_stdvars.sh

Purpose: checks that user-supplied `CC`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, and `LDLIBS` markers propagate into recursive make compile/link commands.

Important logic: reads a build log, skips comments/echoes/blanks, classifies compile lines by ` -c ` and link lines by compiler invocation, then verifies marker flags are present. `report()` records failures.

Control flow/state: accumulates seen/ok counters and exits `1` if any marker is missing; otherwise prints a success summary.

Dependencies/integration: POSIX shell; intended for verbose/dry-run make logs with injected marker variables.

Risks: heuristic command classification can miss unusual compiler wrappers or spacing; validates presence, not argument order.

Test signals: failure output names the exact command missing markers.
