<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Kconfig

## Purpose

This Kconfig file exposes the Atmel HLCDC DRM display-controller driver as `DRM_ATMEL_HLCDC`.

## Important APIs, Types, And Symbols

- `config DRM_ATMEL_HLCDC`: tristate option named "DRM Support for ATMEL HLCDC Display Controller".
- Dependencies: `DRM`, `OF`, `COMMON_CLK`, and either `MFD_ATMEL_HLCDC && ARM` or `COMPILE_TEST`.
- Selects: `DRM_CLIENT_SELECTION`, `DRM_GEM_DMA_HELPER`, `DRM_KMS_HELPER`, and `DRM_PANEL`.

## Control Flow

Kconfig selection controls whether the module objects in the local Makefile are built. There is no runtime control flow.

## State And Persistence Behavior

The symbol persists in kernel configuration and controls module/built-in compilation. It does not store runtime state.

## Dependencies And Integration Points

It ties the DRM display subdriver to the parent Atmel HLCDC MFD, device tree, clocks, DMA GEM helpers, KMS helpers, and panel framework.

## Risks And Edge Cases

The `COMPILE_TEST` path permits non-ARM build coverage without real MFD hardware. Missing selected helpers or parent MFD support will prevent useful runtime probing even if compilation succeeds.

## Test Signals

Kconfig build tests for built-in/module/off states, ARM device-tree probe tests with `MFD_ATMEL_HLCDC`, and `COMPILE_TEST` coverage on other architectures validate the symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Kconfig -->
