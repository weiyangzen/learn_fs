# sources/distributed-fs/ceph-client/drivers/gpu/drm/stm/Makefile

## Purpose
The STM DRM Makefile maps Kconfig symbols to build objects for the LTDC core driver and optional STM display bridge/host modules.

## Important Build Rules
- `stm-drm-y := drv.o ltdc.o`: the core STM DRM module consists of the DRM platform driver and LTDC implementation.
- `obj-$(CONFIG_DRM_STM_DSI) += dw_mipi_dsi-stm.o`: builds the STM DW MIPI DSI wrapper as its own object/module when selected.
- `obj-$(CONFIG_DRM_STM_LVDS) += lvds.o`: builds the STM LVDS bridge when selected.
- `obj-$(CONFIG_DRM_STM) += stm-drm.o`: links the core driver when enabled.

## Control Flow, State, and Persistence
The file has no runtime behavior. Its ordering matters because `drv.o` owns platform probe/module registration while `ltdc.o` provides the core LTDC functions called by `drv.c`.

## Dependencies and Integration Points
It integrates with `drivers/gpu/drm/stm/Kconfig`. Optional objects depend on the Kconfig dependencies already selecting generic MIPI DSI or bridge support.

## Risks and Test Signals
Risk is mainly build-coverage drift: exported functions in `ltdc.h` must stay available to `drv.o`, and optional modules must not assume core objects are linked into the same module. Build tests should cover built-in and module combinations for `DRM_STM`, `DRM_STM_DSI`, and `DRM_STM_LVDS`.
