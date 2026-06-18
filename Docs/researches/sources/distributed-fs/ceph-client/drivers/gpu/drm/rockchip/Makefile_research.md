# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/Makefile

## Purpose
Builds the Rockchip DRM composite object and conditionally includes each display controller/output implementation according to Kconfig.

## Important APIs, Types, And Functions
Defines `rockchipdrm-y` with the core driver, framebuffer, and GEM files. Appends controller/output objects through `rockchipdrm-$(CONFIG_...)` lines, then emits `obj-$(CONFIG_DRM_ROCKCHIP) += rockchipdrm.o`.

## Control Flow
No runtime control flow. Build control determines which C files contribute platform driver symbols referenced by the top-level registration table.

## State And Persistence
No runtime state. The built object composition persists in the kernel build output.

## Dependencies And Integration Points
Must stay synchronized with `Kconfig` and `rockchip_drm_drv.c` `ADD_ROCKCHIP_SUB_DRIVER()` calls. For Cadence DP, both `cdn-dp-core.o` and `cdn-dp-reg.o` are included together.

## Risks
Missing an object for a Kconfig symbol produces undefined references when the core tries to register that subdriver. Adding an object without a matching Kconfig path can produce dead code or unexpected build growth.

## Test Signals
Compile tests across all optional symbols, especially `allyesconfig`, `allmodconfig`, and minimal configurations.
