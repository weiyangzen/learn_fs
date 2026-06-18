<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/statecomp/module.mk.in

## Purpose
Defines the make variables and generated-file relationships for building the `statecomp` source-to-source translator.

## Important APIs, Types, And Functions
Sets `STATECOMP`, `STATECOMPSRC`, and `STATECOMPGEN`; lists `statecomp.c`, `codegen.c`, generated `parser.c`, and generated `scanner.c`; records generated `scanner.c`, `parser.c`, and `parser.h`; and declares `scanner.c` depends on `parser.h` with generated files marked secondary.

## Control Flow
The build system uses this fragment to generate parser/scanner artifacts, compile statecomp, and preserve generated intermediates long enough for dependent rules.

## State And Persistence
No runtime state exists. Build artifacts are parser/scanner generated C and header files.

## Dependencies And Integration Points
Integrates flex/bison output with the OrangeFS build and the `.sm` state-machine compilation pipeline.

## Risks And Test Signals
Risks include stale generated parser/scanner files and missing generator dependencies. A clean build from no generated files and an incremental rebuild after `parser.y` or `scanner.l` changes are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/module.mk.in -->
