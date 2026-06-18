# sources/distributed-fs/orangefs/src/common/events/module.mk.in

Purpose: Conditional build registration for TAU event tracing support.

Important build variables: Under `BUILD_TAU`, adds `pvfs_tau_api.c` and `fmt_fsm.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`. When `@TAU_INCS@` is non-empty, sets per-file compile flags to `-x c++ @TAU_INCS@`.

Control flow/state: Make conditional only; no runtime state.

Dependencies/integration: Integrates TAU tracing into common/server/BMI builds only when configured. The `-x c++` flag is essential because the `.c` files contain C++ constructs.

Risks: Toolchains that do not accept `-x c++` or mixed C/C++ linking may fail. The conditional excludes all event code when `BUILD_TAU` is unset, so consumers must guard references.

Test signals: Configure with and without `BUILD_TAU`; verify TAU include substitution and C++ linkage.
