# File Research: sources/cow-pools/openzfs/cmd/zfs/Makefile.am

This Automake fragment builds the `zfs` userspace CLI under `sbin_PROGRAMS` and adds it to `CPPCHECKTARGETS`.

The program source list is the command implementation set for this directory: `zfs_iter.c`, `zfs_iter.h`, `zfs_main.c`, `zfs_project.c`, `zfs_projectutil.h`, and `zfs_util.h`. The linkage model is direct against OpenZFS userspace libraries: `libzfs.la`, `libzfs_core.la`, `libnvpair.la`, and `$(LTLIBINTL)` for gettext internationalization.

Platform-specific linkage is minimal and explicit. When `BUILD_FREEBSD` is enabled, the CLI also links `-lgeom` and `-ljail`, matching the FreeBSD jail integration compiled in `zfs_main.c`.

Integration notes:
- This file is the build glue for the full `zfs` command, not a standalone module.
- It establishes that `zfs_iter.c` and `zfs_project.c` are part of the same binary as the large `zfs_main.c` command dispatcher.
- The dependency set confirms the command is mostly a thin policy, parsing, traversal, and display layer over `libzfs`, `libzfs_core`, and nvlist APIs.

Risks and maintenance notes:
- Any new command source added under `cmd/zfs` must be included here or in another Automake fragment to enter the binary.
- FreeBSD-only command paths in `zfs_main.c` depend on this conditional link stanza.
