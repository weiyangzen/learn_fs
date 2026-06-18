# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/module.mk.in

## Purpose
Build-system fragment for the experimental BMI InfiniBand transport. It conditionally contributes the common IB method sources and whichever provider-specific source files are enabled by configure.

## Important APIs, Types, And Functions
The make variables are `DIR`, `cfiles`, `apis`, `src`, `LIBSRC`, `SERVERSRC`, `LIBBMISRC`, and per-file `MODCFLAGS_*`. Common sources are `ib-exp.c`, `util-exp.c`, and `mem-exp.c`. `BUILD_IB` adds `vapi-exp.c` and `-DVAPI`; `BUILD_OPENIB` adds `openib-exp.c` and `-DOPENIB`.

## Control Flow
The entire fragment is skipped unless `BUILD_IB` or `BUILD_OPENIB` is non-empty. Enabled sources are path-qualified under `src/io/bmi/bmi_ib_exp` and appended to the library, server, and BMI library source lists. Provider include directories are injected only for their provider files through `@IB_INCDIR@` and `@OPENIB_INCDIR@`. `ib-exp.c` receives compile-time API availability flags through `MODCFLAGS_$(DIR)/ib-exp.c`.

## State And Persistence
This file has no runtime state. Its persistent effect is generated build configuration: which transport provider objects are compiled and which preprocessor symbols select initialization branches in `ib-exp.c`.

## Dependencies And Integration Points
It depends on configure substitutions and top-level OrangeFS make variables. It integrates the shared IB transport into the library, server, and BMI library build products and must stay synchronized with the provider function declarations in `ib-exp.c`.

## Risks And Test Signals
Provider combinations matter: `BUILD_OPENIB` only, `BUILD_IB` only, both, and neither exercise different code paths. Stale provider branches are possible because inactive files are excluded entirely. Build tests should verify include paths, `-DOPENIB`/`-DVAPI` propagation to `ib-exp.c`, and successful linking of `bmi_ib_exp_ops` with the selected provider initializer.
