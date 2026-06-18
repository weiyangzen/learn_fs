# sources/distributed-fs/orangefs/src/client/windows/client-test/Makefile

## Purpose
This Makefile builds the `client-test` executable, primarily for comparing behavior against a Linux kernel module or mounted filesystem target.

## Important APIs, Types, And Functions
Targets compile `client-test.o`, `create.o`, `file-ops.o`, `info.o`, `open.o`, `test-io.o`, `test-support.o`, and `timer.o`, then link `client-test` with `-g` and `-lpthread`. `clean` removes the executable and object files.

## Control Flow
Each object has an explicit compile rule using `cc -o $@ -c $< $(CFLAGS)`. The final link rule uses the object list and `$(LDFLAGS)`.

## State And Persistence
Build outputs are local object files and the `client-test` binary. No runtime state is created by the Makefile itself.

## Dependencies And Integration Points
It assumes a Unix-like build environment, `cc`, pthreads, and the local test support/timer sources. It does not list every header dependency, and it omits modules such as `find.o` even though `test-list.h` can include find tests under `WIN32`.

## Risks And Test Signals
The Makefile is not a Windows build recipe despite living under `windows/client-test`; it compiles the portable/Linux side of the tests. Header dependency coverage is incomplete, so incremental rebuilds can miss changes. Successful `make` is a build signal for the non-Windows test harness, not for Dokany service integration.
