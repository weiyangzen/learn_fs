# sources/distributed-fs/openafs/src/tubik/Makefile.in

## Purpose
Builds pthreaded ubik test/debug utilities from the canonical `src/ubik` sources, especially `udebug`, `utst_server`, and `utst_client`.

## Important APIs, Types, And Functions
Targets generate `utst_int.cs.c`, `utst_int.ss.c`, `utst_int.xdr.c`, and `utst_int.h` via `RXGEN`, then build `utst_server`, `utst_client`, and `udebug`. It defines `LTLIBS` with util, ubik, and cmd libraries and includes pthread build fragments.

## Control Flow
`all` builds the three utilities. Source object rules compile files from `$(UBIK)`. Install/dest only place `udebug` into bindirs when `ENABLE_PTHREADED_UBIK` is `yes`; test clients are build/test artifacts. Clean removes objects, binaries, generated RPC files, and version files.

## State And Persistence
Build output includes generated RPC interface files and utility binaries. Installed persistent artifacts are limited to `udebug` under configured paths when enabled.

## Dependencies And Integration Points
This makefile integrates pthread config, ubik library output, rxgen-generated test interfaces, and OpenAFS install paths. It mirrors part of `src/ubik/Makefile.in` for pthreaded builds.

## Risks And Test Signals
Risks include generated file ordering, divergence from the canonical ubik makefile, and conditional install behavior. Signals are successful generation/build of test interfaces, `udebug` link success, `make test`, and install/dest behavior with pthreaded ubik enabled and disabled.
