# sources/distributed-fs/ceph-client/drivers/clk/sprd/Kconfig

## Purpose
Defines build-time configuration for the Spreadtrum clock framework and supported Spreadtrum SoC clock drivers.

## Important APIs, Types, And Functions
The key symbols are `SPRD_COMMON_CLK`, `SPRD_SC9860_CLK`, `SPRD_SC9863A_CLK`, and `SPRD_UMS512_CLK`. `SPRD_COMMON_CLK` is a tristate selected by `ARCH_SPRD` by default and selects `REGMAP_MMIO`; SoC symbols are gated by `SPRD_COMMON_CLK`.

## Control Flow
Kconfig evaluation first enables the common framework when compiling for Spreadtrum or `COMPILE_TEST`; then it conditionally exposes the SC9860, SC9863A, and UMS512 drivers. Defaults follow `ARM64 && ARCH_SPRD`.

## State And Persistence
No runtime state. The selected symbols persist in the kernel `.config` and decide which objects are built into the kernel or as modules.

## Dependencies And Integration Points
Integrates the Spreadtrum clock subtree with the kernel build system, architecture selection, compile-test coverage, and regmap MMIO support used by `common.c`.

## Risks And Edge Cases
Because SoC drivers are tristate, module/built-in combinations must remain linkable with `clk-sprd.o`. `COMPILE_TEST` can expose missing headers or assumptions on non-SPRD platforms. Forgetting to select `REGMAP_MMIO` would break MMIO-backed registration.

## Test Signals
Expected signals are successful `allyesconfig`/`allmodconfig` and targeted ARM64 Spreadtrum builds, with `clk-sprd.o` and selected SoC objects appearing according to `.config`.
