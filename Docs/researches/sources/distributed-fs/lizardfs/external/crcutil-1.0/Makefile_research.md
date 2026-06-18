# sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile

## Purpose
This is a generated Automake Makefile for the bundled Google crcutil 1.0 package. In this repository it is primarily legacy/vendor build metadata; LizardFS' CMake build usually consumes crcutil sources directly through `external/CMakeLists.txt`.

## Important APIs, Types, and Functions
It defines package/install variables, compiler variables, `AM_CXXFLAGS`/`AM_CFLAGS`, `crcutil_ut` as a check program and test, `usage` as a temporary program, source lists for crcutil code, tests, and examples, pattern rules for `.c` and `.cc`, explicit object rules, `check-TESTS`, distribution targets, install/uninstall targets, and clean/distclean/maintainer-clean targets.

## Control Flow and State
The default `all` target depends on `config.h` and delegates to `all-am`. Build rules compile crcutil implementation files and link `crcutil_ut` and `usage`. `check` builds and runs `crcutil_ut`. Install behavior installs only temporary programs to `${tmpdir}`. Distribution targets create tarballs and run standard Automake distcheck flows.

## Dependencies and Integration Points
It depends on generated autotools files such as `configure`, `config.status`, `config.h.in`, dependency files under `.deps`, GCC/G++, and crcutil source directories. LizardFS CMake does not rely on this Makefile for normal bundled compilation.

## Risks and Edge Cases
As generated vendor output, it contains absolute paths from its original generation environment, old Automake assumptions, and many generated rules that are not maintained manually. It uses SSE/MMX flags and architecture-specific sources, which can fail on unsupported compilers or architectures if this Makefile is used directly. Because CMake builds crcutil separately, changes here may not affect the main build.

## Test Signals
Standalone `make check` would run `crcutil_ut`. In the LizardFS CMake path, the more relevant signal is whether bundled crcutil sources compile and link into LizardFS.
