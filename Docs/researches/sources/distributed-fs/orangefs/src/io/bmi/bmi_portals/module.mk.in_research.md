# sources/distributed-fs/orangefs/src/io/bmi/bmi_portals/module.mk.in

## Purpose
Makefile fragment that adds the OrangeFS BMI Portals transport to selected build products when configure enables Portals support.

## Important APIs, Types, And Functions
The fragment is gated by `BUILD_PORTALS`. It sets `DIR := src/io/bmi/bmi_portals`, declares `cfiles := portals.c`, expands `src`, and appends the source to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`. It also sets directory-specific compiler warning flags and optional include flags for `portals.c` through `MODCFLAGS_$(DIR)/portals.c := @PORTALS_INCS@`.

## Control Flow
During makefile inclusion, nothing is emitted unless `BUILD_PORTALS` is non-empty. When enabled, `portals.c` is compiled into the client library, server sources, and BMI library source sets. GNU C builds get extra warnings while suppressing unused warnings because Portals/Cray headers generate unused-symbol noise.

## State And Persistence
No runtime state is created. The only persistent effect is build-system state: source-list variables and module-specific CFLAGS inherited by the top-level generated makefiles.

## Dependencies And Integration Points
The fragment relies on configure substitutions `BUILD_PORTALS` and `@PORTALS_INCS@`, top-level variables `LIBSRC`, `SERVERSRC`, `LIBBMISRC`, `MODCFLAGS_*`, and the expected OrangeFS makefile convention for `module.mk.in` files. It integrates `bmi_portals/portals.c` with the broader BMI build.

## Risks And Test Signals
If `@PORTALS_INCS@` is empty or stale, `portals.c` may fail to find the correct Portals headers. Warning suppression can hide useful diagnostics from this directory. Build tests should verify configure-disabled builds omit the file, configure-enabled builds compile `portals.c`, and generated makefiles propagate Portals include paths only to the intended source.
