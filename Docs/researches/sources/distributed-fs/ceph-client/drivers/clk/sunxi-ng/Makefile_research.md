# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/Makefile

## Purpose
`sunxi-ng/Makefile` maps Kconfig symbols to the common Allwinner CCU support library and SoC-specific provider objects. It defines the object composition for `sunxi-ccu.o` and creates per-SoC module objects such as `sun20i-d1-ccu.o`, `sun50i-a100-ccu.o`, and `sun4i-a10-ccu.o`.

## Important APIs, Types, And Functions
The build API consists of Kbuild variables:

- `obj-$(CONFIG_SUNXI_CCU) += sunxi-ccu.o` builds the common library.
- `sunxi-ccu-y` aggregates shared clock type implementations: `ccu_common.o`, `ccu_mmc_timing.o`, `ccu_reset.o`, base clock types, phase/SDM support, and multi-factor clocks.
- `obj-$(CONFIG_<SOC>_CCU)` creates one module target per SoC-family provider.
- `<module>-y += ccu-<soc>.o` binds module targets to source files.

## Control Flow
There is no runtime flow. Kbuild uses the selected Kconfig values to compile shared CCU infrastructure and the selected SoC provider modules. At runtime, platform drivers inside the compiled provider objects match device-tree compatibles and call the shared `devm_sunxi_ccu_probe()` path.

The object layout separates the reusable clock operations from the descriptor-heavy SoC files. This allows multiple SoC providers to link against the same `sunxi-ccu` object while still producing separate modules.

## State And Persistence
Build state is persisted in generated object files and modules. There is no runtime state here. The Makefile does determine module names, which affects autoloading, dependency resolution, and packaging.

If `SUNXI_CCU` is modular, the shared `sunxi-ccu` module must be available for SoC provider modules that import the `SUNXI_CCU` namespace.

## Dependencies And Integration Points
The Makefile integrates with `Kconfig`, the source files in this directory, module namespace imports in provider C files, Linux CCF, and reset-controller support. It also integrates with distribution packaging and module autoload through the resulting module names.

For this work item, the relevant mappings are `sun20i-d1-ccu-y += ccu-sun20i-d1.o`, `sun20i-d1-r-ccu-y += ccu-sun20i-d1-r.o`, `sun50i-a100-ccu-y += ccu-sun50i-a100.o`, `sun50i-a100-r-ccu-y += ccu-sun50i-a100-r.o`, and `sun4i-a10-ccu-y += ccu-sun4i-a10.o`.

## Risks
Missing a source object from the matching module target can leave a Kconfig option buildable but functionally empty. Renaming a module target changes module filenames and can affect autoload or packaging. Moving a shared clock implementation out of `sunxi-ccu-y` can produce unresolved symbols in multiple providers.

Because provider modules import the `SUNXI_CCU` namespace, build or module-install tests must catch namespace/export regressions, not just compilation of individual `.o` files.

## Test Signals
Useful signals are successful builds for each selected Kconfig option, expected `.ko` names in the output tree, no unresolved symbols or namespace import warnings, and runtime probe of matching device-tree compatibles. `modinfo` should show dependencies on the common CCU module where applicable.
