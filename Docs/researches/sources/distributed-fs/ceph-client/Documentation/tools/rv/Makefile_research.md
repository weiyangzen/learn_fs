<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/tools/rv/Makefile -->
# sources/distributed-fs/ceph-client/Documentation/tools/rv/Makefile

## Purpose
Documentation Makefile that builds and installs manual pages for RV tools from `rv*.rst` sources.

## Important APIs, Types, And Functions
- Variables: `INSTALL`, `RM`, `RMDIR`, `PREFIX`, `MANDIR`, `MAN1DIR`, `OUTPUT`, `MAN1_RST`, `_DOC_MAN1`, `DOC_MAN1`, and `RST2MAN_OPTS`.
- Pattern rule `$(OUTPUT)%.1: %.rst` converts ReST to manpage output.
- Targets: `man1`, `man`, `clean`, `install`, and `uninstall`.

## Control Flow
The default goal is `man`. `MAN1_RST` is discovered with `wildcard`, transformed into `.1` output names, and built through `rst2man`. The generation rule performs an inline dependency check and emits a package hint before failing if docutils is unavailable.

## State And Persistence
Generated manpages live under `$(OUTPUT)`. `install` writes them to `$(DESTDIR)$(PREFIX)/man/man1`; `uninstall` removes matching installed pages and then prunes the directory if empty.

## Dependencies And Integration Points
Uses the same toolchain and conventions as nearby RTLA documentation: GNU make, shell, docutils `rst2man`, and standard install/remove tools. It is intended to be called by kernel documentation or tools packaging workflows.

## Risks And Edge Cases
The Makefile assumes all `rv*.rst` files are man1 pages and that `OUTPUT` is a prefix path. `TEST_RST2MAN` is unused, and generation depends on shell command lookup rather than make-time package metadata.

## Test Signals
Build with `make OUTPUT=/tmp/rv-docs/`, inspect generated `.1` files, run clean, and exercise staged install/uninstall. Missing `rst2man` should produce the documented hard failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/tools/rv/Makefile -->
