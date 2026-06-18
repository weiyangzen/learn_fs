# sources/distributed-fs/openafs/src/tools/rxperf/Makefile.in

## Purpose
Builds the `rxperf` standalone Rx performance tool. The makefile is intentionally small: it compiles `rxperf.o`, links it statically with the OpenAFS Rx library and crypto/roken/thread libraries, and removes generated artifacts on clean.

## Important APIs, Types, And Functions
Targets are `all`, `rxperf`, empty `install`/`dest`, and `clean`. It includes `Makefile.config` and `Makefile.pthread`, sets `top_builddir`, and defines `LIBS` as `src/rx/liboafs_rx.la`. Linking uses `$(LT_LDRULE_static)`, `$(LIB_hcrypto)`, `$(LIB_roken)`, and `$(MT_LIBS)`.

## Control Flow
`all` depends on `rxperf`. The executable target links the single object with Rx and support libraries. There is no install action from this directory. `clean` invokes libtool cleanup and removes the object and binary.

## State And Persistence
The makefile produces build artifacts `rxperf.o` and `rxperf`; it installs nothing. Persistent configuration is inherited from the generated top-level config and pthread make fragments.

## Dependencies And Integration Points
It is part of the OpenAFS autotools build and depends on libtool rules, configured library variables, pthread settings, and the Rx library target. It exists under `src/tools/rxperf`, outside normal server/client installation flows.

## Risks And Test Signals
The lack of install/dest rules means packaging must not assume `rxperf` is installed. Link failures reveal missing Rx, hcrypto, roken, or thread settings. Useful signals are `make rxperf`, clean idempotence, and successful pthread/non-pthread configured builds.
