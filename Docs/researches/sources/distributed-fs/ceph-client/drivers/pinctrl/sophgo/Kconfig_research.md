# sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/Kconfig

## Purpose
This Kconfig file defines build-time configuration for Sophgo pinctrl drivers. It separates the shared core from SoC-specific front-end drivers and from optional operation families for CV18xx and SG2042-style controllers.

## Important Symbols
`PINCTRL_SOPHGO_COMMON` is a tristate internal common driver that selects generic pinctrl groups, generic pinmux functions, and generic pinconf support. `PINCTRL_SOPHGO_CV18XX_OPS` and `PINCTRL_SOPHGO_SG2042_OPS` are boolean helper-operation selectors. User-visible tristate symbols include `PINCTRL_SOPHGO_CV1800B`, `PINCTRL_SOPHGO_CV1812H`, `PINCTRL_SOPHGO_SG2000`, `PINCTRL_SOPHGO_SG2002`, `PINCTRL_SOPHGO_SG2042`, and `PINCTRL_SOPHGO_SG2044`.

## Control Flow
Kconfig does not execute at runtime. Its dependency and select graph determines which source objects are compiled. Each SoC driver depends on `ARCH_SOPHGO || COMPILE_TEST` and `OF`, selects the common driver, and selects its required operation helper family.

## State and Persistence
There is no runtime state in this file. It persists build policy: which modules can be built, which helpers are linked into the common object, and whether a driver can be modular.

## Dependencies and Integration Points
The file integrates with the kernel configuration system, the Sophgo Makefile, and generic pinctrl framework options. The help text documents module names for the user-visible drivers.

## Risks
Because the helper operation symbols are bool while the drivers are tristate, build combinations must ensure helper objects are linked into the common object when any dependent module is built. Missing `OF` would break probe-time match data, so the explicit dependency is important. Select chains can also pull in generic pinctrl helpers for COMPILE_TEST builds, so compile coverage should include modular and built-in cases.

## Test Signals
Use `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and `ARCH_SOPHGO` builds. Confirm each selected SoC symbol produces its advertised module and that disabling all visible Sophgo SoC symbols omits the common objects.
