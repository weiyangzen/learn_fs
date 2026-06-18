<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/tools/rtla/Makefile -->
# sources/distributed-fs/ceph-client/Documentation/tools/rtla/Makefile

## Purpose
Small documentation Makefile that builds and installs manual pages for RTLA tools from `rtla*.rst` sources.

## Important APIs, Types, And Functions
- Variables: `INSTALL`, `RM`, `RMDIR`, `PREFIX`, `MANDIR`, `MAN1DIR`, `OUTPUT`, `MAN1_RST`, `DOC_MAN1`, and `RST2MAN_OPTS`.
- Pattern rule `$(OUTPUT)%.1: %.rst` runs `rst2man`.
- Targets: `man1`, `man`, `clean`, `install`, and `uninstall`.

## Control Flow
The default `man` target depends on `man1`, which depends on every generated manpage path. The pattern rule checks whether `rst2man` is available and fails with a detailed notice if not. Install creates the man1 directory under `$(DESTDIR)$(MAN1DIR)` and copies generated pages; uninstall removes them and attempts to remove the directory if empty.

## State And Persistence
Generated `.1` files are written under `$(OUTPUT)` and removed by `clean`. `install` persists pages into the requested installation prefix, with `DESTDIR` support for package staging.

## Dependencies And Integration Points
Depends on GNU make, shell utilities, `install`, `rm`, `rmdir`, and docutils `rst2man`. The Makefile follows the style of the kernel tools documentation build and is normally invoked from higher-level documentation or tools targets.

## Risks And Edge Cases
`OUTPUT` must include a trailing directory separator when used as a directory prefix. `TEST_RST2MAN` is computed but unused. Missing `rst2man` is a hard error only when generation is required. Installation with an empty `DOC_MAN1` list can still create a directory.

## Test Signals
Run `make`, `make clean`, `make install DESTDIR=...`, and `make uninstall DESTDIR=...` with and without `rst2man`. Verify every `rtla*.rst` becomes a matching `.1` page under `OUTPUT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/tools/rtla/Makefile -->
