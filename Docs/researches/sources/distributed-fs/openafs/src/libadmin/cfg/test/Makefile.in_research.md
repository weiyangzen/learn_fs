# sources/distributed-fs/openafs/src/libadmin/cfg/test/Makefile.in

## Purpose
This makefile builds the `cfgtest` command-line test driver for the configuration admin library. It is an Autoconf-era OpenAFS makefile fragment that pulls in project config and pthread build rules.

## Important APIs, Types, and Functions
The key target is `cfgtest`, built from `cfgtest.o` and `CFGTESTLIBS`. The library list links admin utility, client admin, cfg admin, BOS admin, VOS admin, KAS admin, PTS admin, auth/rpc libraries, and `libcmd.a`. `test` and `tests` alias the `cfgtest` target. `clean` removes objects, the binary, and core files.

## Control Flow and State
Build flow is simple: include shared make configuration, define the static libraries needed by the test driver, link with `$(AFS_LDRULE)`, and expose conventional test/clean targets.

## Persistence and Side Effects
The makefile creates a local `cfgtest` binary and object files. It reads installed/destination libraries from `$(DESTDIR)` and removes generated outputs on clean.

## Dependencies and Integration Points
It integrates the cfg test driver with almost every libadmin component because `cfgtest.c` exercises configuration, client, BOS, VOS, KAS, and PTS flows. It depends on `Makefile.config`, `Makefile.pthread`, `AFS_LDRULE`, `XLIBS`, and the admin libraries being built/installed in expected locations.

## Risks
The link rule contains `-LDEST/lib/afs`, which appears literal rather than `-L$(DEST)/lib/afs` or `-L$(DESTDIR)/lib/afs`; the explicit archive paths may hide that in normal builds, but it is a suspicious portability signal. Static library ordering matters for this old-style link line. The `# static library` comment is placed on the `CFGTESTLIBS` continuation line and should be checked by make parsing.

## Test Signals
A useful signal is whether `make test` builds `cfgtest` after all listed libraries are present. Link failures identify missing cross-library dependencies in the admin stack. `make clean` should remove only local generated files.
