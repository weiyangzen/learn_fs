# sources/distributed-fs/ceph-client/tools/power/pm-graph/Makefile

## Purpose
Installs the pm-graph Python tools, configs, symlinks, and man pages; there is no build step because the tools are scripts.

## Important APIs, Types, and Functions
Important variables are `DESTDIR`, `BINDIR`, `MANDIR`, `LIBDIR`, `INSTALL`, and `INSTALL_DATA`. Targets are `all`, `install`, `uninstall`, and `help`.

## Control Flow, State, and Persistence
`all` prints that nothing is built. `install` first runs `uninstall`, creates `$(LIBDIR)/pm-graph` and config directories, installs `sleepgraph.py`, `bootgraph.py`, selected config files, creates `bootgraph` and `sleepgraph` symlinks in `$(BINDIR)`, and installs man pages. `uninstall` removes those paths and attempts to remove empty directories. Persistent state is the installed filesystem layout.

## Dependencies and Integration Points
Depends on `/usr/bin/install`, `ln`, `rm`, `rmdir`, Python source files, config files, and man pages in the same directory. It is used by package builds and `install_latest_from_github.sh`.

## Risks and Test Signals
`install: uninstall` can remove existing packaged files before reinstalling, which is risky with shared DESTDIR mistakes. Symlink targets assume `/usr/bin` to `/usr/lib` relative layout. `uninstall` removes all config files under the pm-graph config dir. Test `make DESTDIR=/tmp/pkg install`, symlink validity, uninstall idempotence, and packaging with non-default `LIBDIR`.
