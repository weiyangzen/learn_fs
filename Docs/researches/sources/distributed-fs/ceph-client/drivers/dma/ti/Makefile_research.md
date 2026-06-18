# sources/distributed-fs/ceph-client/drivers/dma/ti/Makefile

## Purpose
This Makefile maps the TI DMA Kconfig symbols to object files and defines the multi-object K3 PSI-L endpoint library.

## Important APIs, Types, and Functions
There are no C APIs. The important build targets are `cppi41.o`, `edma.o`, `omap-dma.o`, `k3-udma.o`, `k3-udma-glue.o`, `dma-crossbar.o`, and `k3-psil-lib.o`. `k3-psil-lib-objs` combines the generic `k3-psil.o` lookup code with SoC maps for AM654, J721E, J7200, AM64, J721S2, AM62, AM62A, J784S4, and AM62P.

## Control Flow
Kbuild includes objects according to the corresponding `CONFIG_*` values. When `CONFIG_TI_K3_PSIL` is enabled, Kbuild links the generic PSI-L implementation and every listed SoC table into one module/object library so runtime `soc_device_match()` can select the correct map.

## State and Persistence
The Makefile has no runtime state. Its persistent effect is object composition and symbol availability, especially the exported `psil_get_ep_config()` and `psil_set_new_ep_config()` functions from the PSI-L library.

## Dependencies and Integration Points
It is paired with `drivers/dma/ti/Kconfig` and the source files in this directory. It integrates with Kbuild's `obj-$(CONFIG_...)` and `*-objs` multi-object module conventions.

## Risks
Adding a new K3 SoC endpoint map requires both an extern in `k3-psil-priv.h`, a match entry in `k3-psil.c`, and an object entry here. Missing any one of those causes either link failure or runtime `-ENOTSUPP`/`-ENOENT` lookups. Object ordering is not functionally complex but must include `k3-psil.o` and all maps under the same library.

## Test Signals
Run Kbuild with `CONFIG_TI_K3_PSIL=y` and `=m`, verify all endpoint-map objects are linked, and check module symbol exports. Build configurations toggling each top-level TI DMA symbol should include only expected objects.
