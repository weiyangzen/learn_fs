# Research: sources/distributed-fs/glusterfs/xlators/storage/posix/Makefile.am

Purpose:
This Automake file delegates the POSIX storage translator build to its `src` subdirectory.

Important APIs, types, and functions:
- `SUBDIRS = src` descends into `xlators/storage/posix/src`.
- `CLEANFILES =` is empty.

Control flow and integration:
The recursive build reaches this file from `xlators/storage/Makefile.am` and then enters `src`, where `posix.la`, source lists, headers, flags, and libraries are declared.

State and persistence behavior:
No runtime state or persistent data is defined. This is build metadata only.

Dependencies:
It depends on the `src` subdirectory and its makefile.

Risks and edge cases:
Future POSIX-level tests, scripts, or generated files outside `src` need explicit `SUBDIRS`, `EXTRA_DIST`, or cleanup declarations here.

Test signals:
Build smoke tests should verify recursive configure/make/make clean reaches `posix/src`.
