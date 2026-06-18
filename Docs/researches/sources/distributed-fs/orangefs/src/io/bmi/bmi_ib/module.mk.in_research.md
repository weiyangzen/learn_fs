# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/module.mk.in

## Purpose
`module.mk.in` is the build-system fragment for the BMI InfiniBand method. It conditionally contributes source files and compiler flags to the OrangeFS build when configure enables legacy VAPI and/or OpenIB support.

## Important APIs, Types, and Functions
This file defines Make variables rather than C APIs. `DIR` points at `src/io/bmi/bmi_ib`. `cfiles` always starts with `ib.c util.c mem.c` when either IB backend is enabled. `BUILD_IB` adds `vapi.c` and `-DVAPI`; `BUILD_OPENIB` adds `openib.c` and `-DOPENIB`. The computed `src` list is appended to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`.

Backend include flags are assigned with `MODCFLAGS_$(DIR)/vapi.c := -I@IB_INCDIR@` and `MODCFLAGS_$(DIR)/openib.c := -I@OPENIB_INCDIR@`. `MODCFLAGS_$(DIR)/ib.c := $(apis)` passes the selected provider macros to the common implementation.

## Control Flow
The outer `ifneq (,$(BUILD_IB)$(BUILD_OPENIB))` prevents any BMI IB files from entering the build unless at least one backend is configured. Within that block, provider-specific conditionals extend the source list and macro list. The top-level make system consumes the accumulated source and per-file CFLAGS variables.

## State and Persistence Behavior
There is no runtime state. The fragment persists configure-time decisions into generated make variables. Build artifacts depend on whether `BUILD_IB`, `BUILD_OPENIB`, `IB_INCDIR`, and `OPENIB_INCDIR` were substituted or set by configure.

## Dependencies and Integration Points
The fragment integrates the `bmi_ib` directory with the repository's top-level build variables. It assumes configure has discovered the proper include directories and that the C sources use `VAPI` and `OPENIB` macros to expose provider initialization functions to `ib.c`.

## Risks and Edge Cases
If both providers are enabled, both backend source files are built and `ib.c` tries OpenIB before VAPI. If include directory substitutions are wrong, backend files fail to compile even though the common files may compile. If neither provider is enabled, no common BMI IB code is built. The file does not add provider libraries itself, so link flags must be supplied elsewhere in the build system.

## Test Signals
Build tests should cover OpenIB-only, VAPI-only, both-provider, and no-provider configurations. The resulting compile commands should show `-DOPENIB` and/or `-DVAPI` only for `ib.c`, and backend-specific include paths only for their respective source files.
