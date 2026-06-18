# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/Makefile

## Purpose

This Makefile contributes AMD Display Core IRQ service objects to the AMDGPU display build. It lists the common `irq_service.o` plus ASIC-generation-specific IRQ service implementations from DCE 6 through DCN 4.2.

## Important APIs, Types, And Functions

Build variables include `IRQ`, `AMD_DAL_IRQ`, per-generation lists such as `IRQ_DCE60`, `IRQ_DCE80`, `IRQ_DCE11`, `IRQ_DCE12`, `IRQ_DCN1`, and later `IRQ_DCN*` variables. Each list is prefixed with `$(AMDDALPATH)/dc/irq/...` and appended to `AMD_DISPLAY_FILES`. `CONFIG_DRM_AMD_DC_SI` gates DCE60/Southern Islands IRQ service inclusion.

## Control Flow

During kbuild evaluation, this file appends object paths for all supported IRQ service generations. The only conditional branch is the SI/DCE60 block. The parent display Makefile consumes `AMD_DISPLAY_FILES` to build the selected objects into the AMD display driver.

## State And Persistence Behavior

There is no runtime state. Persistent build state is the object list determining which IRQ service constructors are available to resource creation and ASIC initialization.

## Dependencies And Integration Points

It depends on `AMDDALPATH`, `AMD_DISPLAY_FILES`, and Kconfig symbols supplied by the parent build. It integrates with the common IRQ service core and all generation-specific constructors used by DC resource pools.

## Risks And Test Signals

Risks include missing object entries for a new ASIC generation, stale object names, or accidentally building DCE60 without the SI config gate. Test signals are successful AMDGPU display builds for SI and non-SI configurations and link-time availability of each generation's `dal_irq_service_*_create` symbol.
