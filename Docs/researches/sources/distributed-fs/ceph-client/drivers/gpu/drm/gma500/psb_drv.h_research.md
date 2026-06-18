# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_drv.h

## Purpose
This is the central private header for the GMA500 driver. It defines driver identity, platform detection macros, MMIO/resource constants, SGX MMU bit definitions, IRQ/register constants, key private structures, chip operation dispatch, subsystem prototypes, and register access helpers.

## Important APIs, Types, and Functions
Core types include `struct psb_intel_opregion`, `struct sdvo_device_mapping`, `struct intel_gmbus`, `struct psb_offset`, `struct psb_pipe`, `struct psb_state`, `struct cdv_state`, `struct psb_save_area`, `struct drm_psb_private`, and `struct psb_ops`. It declares modeset, backlight, GEM, chip ops, CRTC/helper, LVDS, and utility APIs. Inline helpers/macros include `to_drm_psb_private()`, `REG_READ/WRITE`, AUX variants, SGX/VDC read/write macros, and platform tests `IS_PSB`, `IS_MRST`, `IS_CDV`.

## Control Flow
There is no executable driver flow, but the header defines dispatch tables that shape runtime flow. `psb_drv.c` chooses a `psb_ops` implementation, then calls its setup/output/backlight/save/restore/power callbacks while display files use the shared register map and private state.

## State and Persistence Behavior
`drm_psb_private` is the persistent driver state container. It owns PCI resource references, GTT/GEM/MMU state, mapped register bases, IRQ masks, modeset mappings, GMBUS, LVDS/VBT/GCT data, HDMI state, saved registers, OpRegion, power/backlight state, and platform flags. `psb_save_area` stores suspend/resume register snapshots.

## Dependencies and Integration Points
The header includes GTT, BIOS, MMU, Oaktrail, OpRegion, power, Intel display, and register headers. It is shared across almost every GMA500 implementation file and therefore forms the integration contract between PCI core, memory management, display, output, power, and ACPI paths.

## Risks
Because it exposes many internals and macros, changes can have wide blast radius. Register macros assume a local `dev` or `dev_priv` variable name. `PSB_WMSVDX32` references `msvdx_reg`, which is not visible in the shown private struct and may be legacy/dead for this tree. Platform detection depends on PCI device ID bit masks.

## Test Signals
Signals include all GMA500 source files compiling with this header, correct chip-op selection by platform macros, valid register access through VDC/AUX/SGX mappings, and no struct-layout regressions affecting suspend/resume or output setup.
