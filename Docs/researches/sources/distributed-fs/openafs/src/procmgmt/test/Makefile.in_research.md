# sources/distributed-fs/openafs/src/procmgmt/test/Makefile.in

## Purpose
Builds the process-management test executable `pmgttest`.

## Important APIs, Types, And Functions
Defines `LIBPMGT=DEST/lib/afs/libprocmgmt.a`, a `pmgttest` link target using `pmgttest.o`, `libprocmgmt.a`, `-lm`, and `${XLIBS}`, plus `test`/`tests` aliases and `clean`.

## Control Flow
`test` or `tests` builds `pmgttest`; it does not run the test. The link uses `$(AFS_LDRULE)`. `clean` removes objects, executable, and core files.

## State And Persistence
Build artifacts are `pmgttest.o` and `pmgttest`.

## Dependencies And Integration Points
Depends on OpenAFS config/LWP make fragments and the process-management archive from `DEST/lib/afs`. The test source exercises the library's public API.

## Risks And Test Signals
Risks include the suspicious `DEST/lib/afs/libprocmgmt.a` literal relative path and test target not executing the binary. Test signals are successful link and manual execution showing all tests pass.
