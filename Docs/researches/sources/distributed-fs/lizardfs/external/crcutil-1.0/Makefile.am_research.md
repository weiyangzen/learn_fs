# sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile.am

## Purpose
This is the concise Automake source file that generated the crcutil `Makefile`. It describes compiler flags, test binary sources, and example usage program sources for standalone crcutil builds.

## Important APIs, Types, and Functions
It sets `AM_CXXFLAGS` to enable CRCUTIL's MM CRC32 mode, warnings, SSE2, and `-Icode`; mirrors that into `AM_CFLAGS`; declares `crcutil_ut` as both `check_PROGRAMS` and `TESTS`; sets `tmpdir=/tmp`; declares `usage` as a temporary program; and lists all crcutil, test, and example sources.

## Control Flow and State
Automake consumes this file to produce the much larger `Makefile.in`/`Makefile` logic. It has no runtime control flow.

## Dependencies and Integration Points
It depends on crcutil source directories `code/`, `tests/`, and `examples/`, plus Automake/autoconf when regenerating vendor build files. The main LizardFS CMake build does not read this file directly.

## Risks and Edge Cases
The hard-coded `-msse2` and CRC mode are architecture-specific. Standalone build behavior can diverge from LizardFS CMake's bundled crcutil target. Regenerating autotools files may change the generated Makefile substantially.

## Test Signals
Standalone `make check` should build and run `crcutil_ut`. CMake builds of bundled crcutil provide the integration-level signal for LizardFS.
