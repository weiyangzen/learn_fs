# sources/distributed-fs/ceph-client/drivers/clk/sophgo/Kconfig

## Purpose
This Kconfig file exposes Sophgo clock-controller drivers for CV1800/CV18xx, SG2042, and SG2044 families. It declares build-time feature switches and dependency relationships between PLL, clock-generator, and subsystem gate drivers.

## Important APIs, Types, And Functions
The symbols are `CLK_SOPHGO_CV1800`, `CLK_SOPHGO_SG2042_PLL`, `CLK_SOPHGO_SG2042_CLKGEN`, `CLK_SOPHGO_SG2042_RPGATE`, `CLK_SOPHGO_SG2044`, and `CLK_SOPHGO_SG2044_PLL`. SG2042 CLKGEN depends on SG2042 PLL; SG2042 RPGATE depends on SG2042 CLKGEN. SG2044 PLL selects `MFD_SYSCON` and `REGMAP_MMIO` because it uses a parent syscon regmap.

## Control Flow
Kconfig controls which objects the Makefile builds. There is no runtime code, but dependency edges enforce that downstream SG2042 providers are not built without their upstream clock providers.

## State And Persistence
No runtime state is stored. The selected symbols determine module/built-in availability and therefore whether matching Device Tree nodes can bind.

## Dependencies And Integration Points
All symbols depend on `ARCH_SOPHGO || COMPILE_TEST` except chained SG2042 subdrivers, which depend on the upstream Sophgo clock symbols. The file integrates with `drivers/clk/sophgo/Makefile` and Device Tree-compatible platform drivers in the same directory.

## Risks
If a downstream symbol lacks a dependency on its upstream clock provider, consumers may get unresolved parent clocks at runtime. The SG2044 help text has a typo (`mulitple`) but the functional dependency is correct. Modular combinations need testing because these are tristate symbols.

## Test Signals
Run `allyesconfig`, `allmodconfig`, and `COMPILE_TEST` builds. Runtime tests should verify module autoload and probe ordering for SG2042 PLL -> CLKGEN -> RPGATE and SG2044 PLL plus main clock controller.
