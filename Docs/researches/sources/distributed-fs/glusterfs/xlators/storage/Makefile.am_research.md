# Research: sources/distributed-fs/glusterfs/xlators/storage/Makefile.am

Purpose:
This Automake file declares the storage translator subtree. It has one child directory, `posix`, and no generated cleanup files.

Important APIs, types, and functions:
- `SUBDIRS = posix` makes the storage build descend into the POSIX storage translator.
- `CLEANFILES =` is empty.

Control flow and integration:
During recursive Automake builds, the parent `xlators` build enters `xlators/storage`, then delegates substantive storage translator build work to `xlators/storage/posix`.

State and persistence behavior:
No runtime state or persistent data is defined. This is build graph metadata only.

Dependencies:
It depends on the `posix` subdirectory and its makefile.

Risks and edge cases:
Adding another storage backend requires updating `SUBDIRS`; otherwise source may exist but not build. Generated files added at this level need explicit cleanup rules.

Test signals:
Verify `make`, `make clean`, and distribution targets traverse the intended storage subdirectories.
