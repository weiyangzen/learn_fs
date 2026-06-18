# File Research: sources/block-storage/parted/libparted/Makefile.am

This Automake file defines the build for `libparted.la`, the main libparted shared library.

Key points:
- Conditionally adds the `tests` subdirectory when `HAVE_CHECK` is enabled.
- Selects one architecture backend through `ARCH_SOURCE = arch/$(OS).c`.
- Builds subdirectories in this order: `labels`, `fs`, current directory, and optional tests.
- Main library sources are `debug.c`, `architecture.c`, `architecture.h`, `device.c`, `exception.c`, `filesys.c`, `libparted.c`, `timer.c`, `unit.c`, `disk.c`, `cs/geom.c`, `cs/constraint.c`, `cs/natmath.c`, and the selected architecture source.
- `EXTRA_libparted_la_SOURCES` lists all possible architecture backends: Linux, GNU/Hurd, and BeOS.
- Links filesystem and disk-label sublibraries plus gnulib and optional OS/device-mapper/blkid/uuid/intl libraries.
- Uses libtool version-info `2:5:0`.

Research notes:
- This file is the build-time switchboard that determines which `PedArchitecture` implementation is compiled as the active platform backend.
- `arch/linux.h` is listed as an extra source because it is Linux-backend private support, not a public installed header.
