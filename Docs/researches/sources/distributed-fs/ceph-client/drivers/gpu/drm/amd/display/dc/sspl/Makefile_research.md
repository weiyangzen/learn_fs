<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/Makefile

## Purpose

The SSPL Makefile adds the scaler programming library to the AMD Display build. SSPL calculates scaler, EASF, and iSHARP programming data used by DCN display pipes.

## Important APIs, Types, And Functions

- `SPL = dc_spl.o dc_spl_scl_filters.o dc_spl_scl_easf_filters.o dc_spl_isharp_filters.o dc_spl_filters.o spl_fixpt31_32.o spl_custom_float.o`.
- `AMD_DAL_SPL = $(addprefix $(AMDDALPATH)/dc/sspl/,$(SPL))`.
- `AMD_DISPLAY_FILES += $(AMD_DAL_SPL)`.

## Control Flow

Kbuild expands the SSPL object list, prefixes each object with the display source path, and appends them to the driver object list.

## State And Persistence Behavior

No runtime state exists. The file controls which SSPL compilation units are linked into the display driver.

## Dependencies And Integration Points

It depends on `AMDDALPATH` and `AMD_DISPLAY_FILES`. It integrates the core SPL calculator, fixed-point math, custom float conversion, standard scaler filters, EASF filter tables, iSHARP filter tables, and filter conversion helpers.

## Risks And Edge Cases

Leaving out one object can compile the public headers but fail at link time or disable a required filter path. Adding new public SPL APIs usually requires updating this object list.

## Test Signals

Build/link tests should resolve `spl_calculate_scaler_params`, filter lookup helpers, fixed-point math helpers, and iSHARP/EASF support. Runtime scaler tests indicate whether the full object set is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/Makefile -->
