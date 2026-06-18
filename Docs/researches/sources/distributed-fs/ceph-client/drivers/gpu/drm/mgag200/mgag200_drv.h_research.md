# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_drv.h

## Purpose
Defines the shared mgag200 driver ABI: register access macros, driver metadata, device state structures, chip capability tables, PLL state, and cross-file function prototypes.

## Important APIs, types, and functions
- MMIO/DAC/VGA indexed register macros: `RREG8`, `WREG8`, `RREG32`, `WREG32`, `RREG/WREG_*` for MISC, ATTR, SEQ, CRT, ECRT, GFX, and DAC.
- `MGAG200_DAC_DEFAULT()` centralizes default DAC register tables used by chip-specific init files.
- `struct mgag200_pll_values` stores m/n/p/s PLL parameters.
- `struct mgag200_crtc_state` extends `drm_crtc_state` with primary format, PIXPLLC values, and BMC video-reset flag.
- `enum mga_type` enumerates PCI-dispatched chip variants.
- `struct mgag200_device_info` captures max mode size, bandwidth cap, BMC sync flag, I2C GPIO bits, and `bug_no_startadd`.
- `struct mgag200_device_funcs` supplies per-chip PLL atomic check/update callbacks.
- `struct mga_device` embeds the DRM device and core resources/output objects.
- Helper macros assemble shared plane and CRTC function tables.

## Control flow
Header macros expand into indexed MMIO register operations used throughout the driver. The function table macros define the common atomic helper behavior used by per-chip pipeline initialization.

## State and persistence
The structures define persistent driver state for the DRM device lifetime. Register macros mutate persistent hardware state and depend on a local `mdev` variable convention in callers.

## Dependencies and integration points
Includes DRM connector/CRTC/encoder/GEM/plane headers and `mgag200_reg.h`. All mgag200 C files depend on this header for shared types and prototypes.

## Risks
The register macros are not type-safe and assume `mdev` exists in scope. Indexed DAC/VGA access is shared by DDC, modesetting, BMC, and PLL paths and must be serialized. `MGAG200_DAC_DEFAULT()` is a dense table of magic values that affects every chip init path.

## Test signals
Build coverage across all variants, lockdep/race testing around MMIO access, and runtime modeset/EDID/PLL validation all exercise this header's contracts.
