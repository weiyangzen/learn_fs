# sources/compression/lz4/lib/liblz4.pc.in

## Purpose
This pkg-config template describes how downstream builds should compile and link against installed `liblz4`.

## Important Fields
Template variables are `@PREFIX@`, `@LIBDIR@`, `@INCLUDEDIR@`, and `@VERSION@`. The generated file exposes `Name: lz4`, description, project URL, `License: BSD-2-Clause`, `Version`, `Libs: -L${libdir} -llz4`, and `Cflags: -I${includedir}`.

## Control Flow
`lib/Makefile` substitutes paths and version, including a pass to preserve `${prefix}` variable references in generated path values. The generated `liblz4.pc` is installed under the configured pkg-config directory.

## State and Persistence
The template itself has no runtime state. The generated `.pc` file becomes installed build metadata for downstream projects.

## Dependencies and Integration Points
It integrates with `pkg-config`, distribution packaging, and `make install`. It depends on the library actually being installed in the substituted `libdir` and headers in `includedir`.

## Risks
Incorrect prefix/libdir substitution breaks downstream discovery. The template does not include private libraries, which is fine for current LZ4 but would need review if link dependencies are added.

## Test Signals
After `make install DESTDIR=<tmp>`, run `pkg-config --cflags --libs` against the generated file with `PKG_CONFIG_PATH` pointed at the temporary pkgconfig directory.
