# sources/distributed-fs/ceph-client/drivers/clk/pistachio/Kconfig

Purpose: Defines the config symbol for IMG Pistachio SoC clock-controller support.

Important APIs, types, and functions: `COMMON_CLK_PISTACHIO` is a bool depending on `MIPS || COMPILE_TEST`. Help text says to enable clock support for the IMG Pistachio SoC.

Control flow: Kconfig enables building the Pistachio clock support objects through parent Makefile logic.

State and persistence: No runtime state; this is configuration-only.

Dependencies and integration points: Allows native MIPS builds and compile-test coverage elsewhere.

Risks: As a bool, the driver is built-in when selected, matching the early `CLK_OF_DECLARE()` style used by the implementation. There is no per-subcontroller config split.

Test signals: `COMPILE_TEST=y` should allow building on non-MIPS architectures. Pistachio platform configs should select or enable this symbol so early clock providers exist.
