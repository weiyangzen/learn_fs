# sources/distributed-fs/glusterfs/xlators/features/utime/src/Makefile.am

## Purpose
Builds the `utime.la` translator and generates its fop wrapper source/header from templates.

## Important APIs, Types, and Functions
- `AUTOMAKE_OPTIONS = subdir-objects`.
- `utime_sources` includes `utime-helpers.c` and `utime.c`.
- `nodist_utime_la_SOURCES = utime-autogen-fops.c utime-autogen-fops.h`.
- `BUILT_SOURCES = utime-autogen-fops.h`.
- Python generators create `.c` and `.h` outputs from templates when `#pragma generate` is encountered.
- Links `libglusterfs.la`, includes `xlators/lib/src`, and removes installed `utime.so` in `uninstall-local`.

## Control Flow
During build, `utime-gen-fops-c.py` and `utime-gen-fops-h.py` expand templates before compiling the module.

## State and Persistence
Generated files are build artifacts and cleaned through `CLEANFILES`.

## Dependencies and Integration Points
Depends on Python, libglusterfs generator module, `libxlator.h`, GlusterFS headers, and build variables. The generated wrappers are required by `utime.c` fops registration.

## Risks
Generator/template drift can cause missing fop symbols. Python path assumes relative location to `libglusterfs/src`.

## Test Signals
Clean build from generated sources, `make clean`, and verifying all fops referenced in `utime.c` are generated.
