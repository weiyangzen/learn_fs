# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/Makefile

## Purpose
This Makefile maps Marvell Ethernet Kconfig symbols to object files and child directories built by Kbuild.

## Important Entries
The file builds `mvmdio.o`, `mv643xx_eth.o`, `mvneta_bm.o`, `mvneta.o`, `pxa168_eth.o`, `skge.o`, and `sky2.o` based on their matching `CONFIG_*` symbols. It descends into `mvpp2/` when `CONFIG_MVPP2` is enabled. It always descends into `octeon_ep/`, `octeon_ep_vf/`, `octeontx2/`, and `prestera/`; those subdirectories are expected to gate their own objects internally.

## Control Flow
During Kbuild, `obj-$(CONFIG_...)` expands to built-in, module, or omitted objects. `obj-y` subdirectories are visited unconditionally as part of the Marvell vendor tree, allowing child Makefiles to evaluate their own config-controlled objects.

## State And Persistence
There is no runtime state. Build state comes from `.config`, generated Kbuild variables, and child Makefile decisions.

## Dependencies And Integration Points
It integrates directly with `marvell/Kconfig` symbols and the source files/subdirectories in the Marvell Ethernet driver tree. It also relies on child directories having Makefiles that correctly handle disabled configs because several are entered through unconditional `obj-y`.

## Risks
The unconditional subdirectory descent can expose child Makefile errors even when a feature is disabled. Renaming a driver source or changing a Kconfig symbol without updating this file breaks build coverage. The `mvpp2/` directory is conditional while Octeon/Prestera directories are unconditional, so maintainers need to preserve the intended split when adding new Marvell families.

## Test Signals
Build with each Marvell symbol as `y`, `m`, and unset where legal. Run `make M=drivers/net/ethernet/marvell` style module builds if supported by the source tree, plus randconfig to catch stale object names or child-directory dependency problems.
