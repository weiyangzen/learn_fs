# sources/distributed-fs/openafs/src/afsmonitor/Makefile.in

## Purpose

`Makefile.in` defines the build, install, and clean rules for `afsmonitor` and the auxiliary `afsmon-parselog` tool.

## Important Targets and Variables

`INCLS` lists GTX, keys, cellconfig, cmd, xstat, and local monitor headers. `LT_deps` links xstat, gtx, rxkad, fsint, cmd, util, opr, lwp compatibility, and volser libraries. `EXTRA_LIBS` adds curses and X libraries. Targets include `all`, object rules, `afsmonitor`, `afsmon-parselog`, `install`, `dest`, and `clean`.

## Control Flow

Configure substitutes paths and included make fragments. `all` builds `afsmonitor`; explicit targets link monitor/parser binaries; install targets create destination directories and install `afsmonitor`; clean removes libtool artifacts, objects, the binary, and generated version source.

## State and Persistence Behavior

The makefile creates local build products and installed binaries. It includes version-generation support through `Makefile.version`.

## Dependencies and Integration Points

The monitor integrates with OpenAFS xstat collection, GTX UI, curses/X display support, command parsing, Rx/Rxkad, and utility libraries.

## Risks and Test Signals

The `afsmon-parselog` link rule names `afsmon-parselog.o` as a dependency but compiles `afsmon-parselog.c` in the link command, which is unusual. Manual header dependencies can become stale. Test `make afsmonitor`, `make afsmon-parselog`, `make clean`, staged install, and rebuilds after touching local headers.
