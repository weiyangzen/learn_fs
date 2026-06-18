# sources/distributed-fs/coda/coda-src/util/daemonizer.h

## Purpose
Declares daemonization and pidfile helpers for Coda daemons.

## Important APIs, Types, And Functions
The public C API is `daemonize()`, `update_pidfile(const char *)`, and `gogogo(int)`.

## Control Flow
Callers typically call `daemonize()`, perform initialization, call `update_pidfile()`, redirect logs as desired, then call `gogogo(parent_fd)` when ready.

## State And Persistence
The API manages pidfile and lockfile state through the implementation; no state is visible in the header.

## Dependencies And Integration Points
The header is C/C++ compatible and used by daemon programs across the Coda tree.

## Risks
Readiness notification is caller-driven, so incorrect ordering can report success before the service is actually listening or leave the parent blocked.

## Test Signals
Compile from C and C++, run daemon startup success/failure paths, and verify pidfile lock lifetime.
