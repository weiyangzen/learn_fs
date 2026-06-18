# sources/distributed-fs/ceph-client/drivers/edac/Makefile Research

## Purpose
This Makefile maps EDAC Kconfig symbols to kernel objects. It builds the EDAC core, optional core feature objects, MCE decoder support, and individual hardware EDAC drivers.

## Important APIs, Types, and Functions
There are no runtime APIs. The important build targets are `edac_core.o`, `edac_mce_amd.o`, `amd64_edac.o`, `al_mc_edac.o`, `amd76x_edac.o`, `altera_edac.o`, and `a72_edac.o`. Composite objects include `mpc85xx_edac_mod-y`, `layerscape_edac_mod-y`, `skx_edac_common-y`, `skx_edac-y`, `i10nm_edac-y`, and `imh_edac-y`.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` assignments after Kconfig selection. `CONFIG_EDAC` builds `edac_core.o` from memory-controller, device, module, sysfs, and workqueue sources. `CONFIG_PCI` conditionally adds EDAC PCI core files. Optional feature symbols append debugfs, scrub, ECS, and memory repair objects. Hardware-specific symbols then append their driver object files.

## State and Persistence
The Makefile persists no runtime state. It determines build artifacts: built-in objects for `y`, modules for `m` where allowed by Kconfig, and omitted objects for unset symbols.

## Dependencies and Integration Points
The file integrates directly with the symbols declared in `drivers/edac/Kconfig`. It also encodes shared-object relationships, such as Intel SKX/I10NM/IMH drivers sharing `skx_edac_common.o`, and Freescale/Layerscape drivers sharing `fsl_ddr_edac.o`.

## Risks and Edge Cases
Symbol/object drift is the main risk: adding a Kconfig option without a Makefile entry yields an unbuildable or unreachable driver, while a Makefile entry with missing Kconfig gating can build on unsupported platforms. Shared objects can create link surprises if multiple related drivers are built with incompatible built-in/module settings.

## Test Signals
Run targeted kernel builds with `CONFIG_EDAC=y`, `CONFIG_EDAC_DEBUG=y`, `CONFIG_EDAC_AMD64=m`, `CONFIG_EDAC_AL_MC=m`, `CONFIG_EDAC_AMD76X=m`, `CONFIG_EDAC_ALTERA=y`, and `CONFIG_EDAC_CORTEX_A72=m` as architecture-appropriate. Kbuild output should include the expected `.o` or `.ko` files and no unresolved symbols from optional core pieces.
