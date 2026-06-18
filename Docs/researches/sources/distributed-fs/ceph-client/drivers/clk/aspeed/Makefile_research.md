# sources/distributed-fs/ceph-client/drivers/clk/aspeed/Makefile

Purpose: this Makefile builds Aspeed clock controller objects for supported SoC generations.

Important build rules: `clk-aspeed.o` is built for `COMMON_CLK_ASPEED`, `clk-ast2600.o` for `MACH_ASPEED_G6`, and `clk-ast2700.o` for `COMMON_CLK_AST2700`.

Control flow/state: no runtime state; object selection determines which platform/OF clock providers are linked.

Dependencies and risks: AST2600 build is tied to the machine symbol, not a local Kconfig option. The common header `clk-aspeed.h` is shared by the older and AST2600 drivers. Test signals are defconfig builds for each generation, compile-test builds, and ensuring no unused generation object is required by another.
