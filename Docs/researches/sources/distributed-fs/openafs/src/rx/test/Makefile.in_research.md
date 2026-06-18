# sources/distributed-fs/openafs/src/rx/test/Makefile.in

## Purpose
Builds RX test programs for LWP and selected pthread/multithreaded variants.

## Important APIs, Types, And Functions
It includes `Makefile.config` and `Makefile.lwp`, defines library paths and `LIBS`, sets `MODULE_CFLAGS=-DRXDEBUG`, lists `RXTESTOBJS`, `BASICINCLS`, link macros, LWP test binaries (`testclient`, `testserver`, `kstest`, `kctest`, `tableGen`, `generator`), pthread binaries (`th_testserver`, `th_testclient`), and `clean`.

## Control Flow
`all` builds both `test` and `th_test`. Individual LWP binaries link against local `../librx.a`, LWP, command, util, sys, OPR, crypto, roken, and platform libraries. Threaded test objects compile `testclient.c`/`testserver.c` with `MT_CC`/`MT_CFLAGS` and link against `libafsrpc.a`. Object dependencies force rebuilds when core RX headers change.

## State And Persistence
Build artifacts are object files, archives, binaries, and possible core files. `clean` removes these artifacts.

## Dependencies And Integration Points
The makefile integrates RX unit/integration test sources with the OpenAFS build system, LWP RX library, pthread RX library, and debug compilation. It references `rx_clock.h`, `rx_queue.h`, `rx_event.h`, and `rx.h` as basic dependencies.

## Risks And Test Signals
Risks include Solaris-specific comments around threaded link lines, library-order sensitivity, stale dependencies that omit newer headers, and debug-only behavior due to `RXDEBUG`. Successful `make test`, `make th_test`, and running client/server test pairs are the main signals.
