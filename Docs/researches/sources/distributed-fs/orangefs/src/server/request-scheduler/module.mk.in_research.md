# sources/distributed-fs/orangefs/src/server/request-scheduler/module.mk.in

## Purpose
This makefile fragment wires the OrangeFS request scheduler into the build. It defines the request-scheduler source directory and adds `request-scheduler.c` to the library and, when server builds are enabled, to the server source list.

## Important APIs, Types, and Functions
There are no runtime APIs. Build variables are `BUILD_SERVER`, `DIR`, `LIBSRC`, and `SERVERSRC`.

## Control Flow and State
The file is processed by the build system. `request-scheduler.c` is always included in `LIBSRC`; `ifdef BUILD_SERVER` also appends it to `SERVERSRC`.

## State and Persistence Behavior
No runtime state or persistence.

## Dependencies and Integration Points
The fragment assumes autoconf substitutes `@BUILD_SERVER@` and that the parent build includes module fragments that aggregate `LIBSRC` and `SERVERSRC`.

## Risks and Edge Cases
Duplication between library and server source lists can matter if build rules compile the same translation unit into multiple targets. Incorrect `BUILD_SERVER` substitution can omit scheduler symbols from server binaries.

## Test Signals
Coverage is build-level: successful server/library compilation and link resolution for request scheduler functions.
