# sources/distributed-fs/ceph-client/drivers/reset/sti/Kconfig

Purpose: Kconfig gate for STiH407 reset driver support.

Important APIs/types/functions: `STIH407_RESET` is a bool visible under `COMPILE_TEST` and enabled only within `ARCH_STI || COMPILE_TEST`.

Control flow: build-time only; selects whether STiH407 reset objects are compiled.

State and persistence: generated kernel config is the only state.

Dependencies and integration: scoped to STi architecture or compile testing; object mapping is in the adjacent Makefile.

Risks and test signals: no explicit dependency on syscon/regmap because those are generally available subsystems; build tests under COMPILE_TEST catch missing includes or symbol drift.
