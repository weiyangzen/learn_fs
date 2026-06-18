# sources/distributed-fs/lustre-release/lnet/utils/Makefile.am

## Purpose
Defines the Automake build for LNet user-space utilities and pkg-config installation.

## Important Build Targets
Builds subdir `lnetconfig`, installs `lnet.pc`, and under `UTILS` builds `routerstat`, `lst`, and `lnetctl`. Under `TESTS`, also builds `wirecheck`.

## Control Flow
Automake conditionals decide which programs are compiled. Top-level utilities link against `lnetconfig/liblnetconfig.la`; `lst` and `lnetctl` also use libnl, yaml, and optional efence.

## State And Persistence
No runtime state. The file affects generated Makefiles, build artifacts, and installed pkg-config metadata.

## Dependencies And Integration Points
Depends on configure-provided utility, libnl3, yaml, and efence flags plus the lnetconfig library.

## Risks
`lst_CFLAGS` overrides common flags and must stay in sync where needed. Missing yaml/libnl dependencies break utility links. Conditional configurations need coverage.

## Test Signals
Build with `UTILS` on/off and `TESTS` on/off, verify links for all utilities, and verify `lnet.pc` installation.
