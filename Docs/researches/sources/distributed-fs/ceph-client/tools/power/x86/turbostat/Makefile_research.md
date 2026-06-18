# sources/distributed-fs/ceph-client/tools/power/x86/turbostat/Makefile

## Purpose
The `turbostat/Makefile` builds, installs, cleans, and packages the `turbostat` x86 power diagnostic tool. It is a compact standalone build recipe that supports out-of-tree output through `O=`, cross-compilation through `CROSS_COMPILE`, install prefix staging through `PREFIX` and `DESTDIR`, and snapshot tarball creation for distributing `turbostat` with the required kernel header fragments.

## Important Targets And Variables
Core variables are `CC=$(CROSS_COMPILE)gcc`, `BUILD_OUTPUT=$(CURDIR)` or `$(O)`, `PREFIX?=/usr`, `DESTDIR?=`, `DAY=$(shell date +%Y.%m.%d)`, and `SNAPSHOT=turbostat-$(DAY)`. The explicit target `turbostat : turbostat.c` relies on the pattern rule `%: %.c`, which creates `$(BUILD_OUTPUT)` and links with `-lcap -lrt`. `override CFLAGS` appends optimization, warnings, include paths, file-offset support, fortify, and preprocessor definitions pointing to kernel headers. Phony targets are `clean`, while `install` and `snapshot` are regular make targets.

## Control Flow
`make turbostat` compiles `turbostat.c` into `$(BUILD_OUTPUT)/turbostat`. `make clean` removes the built binary and current snapshot archive. `make install` builds first, then installs the binary into `$(DESTDIR)$(PREFIX)/bin` and the manual page into `$(DESTDIR)$(PREFIX)/share/man/man8`. `make snapshot` builds, creates a dated snapshot directory, copies source/man/build files and `intel-family.h`, transforms `msr-index.h` to use local generated `bits.h`, writes minimal local `bits.h` and `build_bug.h`, generates a snapshot Makefile with local header definitions, appends the original Makefile with kernel-header definition lines removed, and tars the snapshot.

## State And Persistence Behavior
Build outputs are written to `$(BUILD_OUTPUT)`, which defaults to the source directory but can be redirected with `O=...`. Installation writes under `DESTDIR/PREFIX`. Snapshot state is written into `turbostat-YYYY.MM.DD/` and `turbostat-YYYY.MM.DD.tar.gz` in the current directory, with previous same-day snapshot directories removed first.

## Dependencies And Integration Points
The build depends on a C compiler, kernel include paths relative to the tool directory, libcap, librt, and the `turbostat.8` man page. The snapshot target integrates selected Linux headers into a distributable local include set so the snapshot can build outside the full kernel tree.

## Risks And Edge Cases
`override CFLAGS +=` means caller-supplied CFLAGS are augmented rather than replacing the Makefile requirements, which is usually desirable but can surprise packaging. The generic `%: %.c` rule can build any C source in the directory, not only turbostat. Snapshot naming is date-based, so repeated snapshots on the same day overwrite the directory and archive. Relative kernel header paths assume the source tree layout remains unchanged. Snapshot header generation uses shell `echo` and `sed` commands whose quoting is important.

## Test Signals
Run `make clean`, `make turbostat`, `make O=/tmp/turbostat-build turbostat`, `make install DESTDIR=/tmp/pkg PREFIX=/usr`, and `make snapshot` in a full kernel source tree. Verify the linked binary exists in `BUILD_OUTPUT`, install paths are correct, and the snapshot tarball contains generated `bits.h`, `build_bug.h`, transformed `msr-index.h`, `intel-family.h`, source, man page, and a self-contained Makefile.
