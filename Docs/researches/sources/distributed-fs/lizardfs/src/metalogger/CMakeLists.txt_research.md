# sources/distributed-fs/lizardfs/src/metalogger/CMakeLists.txt

## Purpose

`src/metalogger/CMakeLists.txt` builds the LizardFS metalogger library, tests, and `mfsmetalogger` executable. The source was read as a complete 17-line CMake file.

## Important APIs, Types, and Functions

It sets include directories, defines `METALOGGER`, `APPNAME=mfsmetalogger`, and examples subdir, collects sources, builds a `metalogger` library with local sources plus `../master/changelog.cc` and `../master/masterconn.cc`, links `mfscommon`, creates unit tests, builds `mfsmetalogger` from `${MAIN_SRC}`, optionally links PAM/systemd, and installs the executable.

## Control Flow

CMake configure flow collects source lists and declares library/test/executable targets. Build flow links shared master connection/changelog code into metalogger.

## State and Persistence Behavior

No runtime persistence is defined here. The resulting metalogger binary persists metadata/changelog data according to its source code.

## Dependencies and Integration Points

It integrates metalogger with common code, master connection code, authentication/systemd libraries, and the project install/test macros.

## Risks and Edge Cases

Directly including master source files creates tight coupling between master and metalogger builds. Compile definitions alter shared code behavior, so tests must cover the `METALOGGER` variant. Optional systemd/PAM linking can change deployment dependencies.

## Test Signals

Build target success, `create_unittest(metalogger ...)` execution, packaging/install checks, and smoke tests connecting a metalogger to a master.
