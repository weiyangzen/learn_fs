## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_sideband.h

### Purpose

`vlv_sideband.h` provides typed convenience wrappers for VLV/CHV IOSF sideband units used by display code: BUNIT, CCK, CCU, DPIO, FLISDSI, NC, and PUNIT.

### Important APIs, types, and functions

Inline APIs include `vlv_bunit_get/read/write/put()`, `vlv_cck_get/read/write/put()`, `vlv_ccu_get/read/write/put()`, `vlv_dpio_get/read/write/put()`, `vlv_flisdsi_get/read/write/put()`, `vlv_nc_get/read/put()`, and `vlv_punit_get/read/write/put()`. Real DPIO access is declared when `I915` is enabled; otherwise stubs return zero or do nothing.

### Control flow

Each wrapper calls `vlv_iosf_sb_get()` with the bit for the unit, performs `vlv_iosf_sb_read()` or `vlv_iosf_sb_write()` with the unit ID, and releases through `vlv_iosf_sb_put()`. Multi-unit DPIO get/put covers both DPIO units.

### State and persistence behavior

The header stores no software state. It controls access to persistent sideband register state and participates in sideband unit locking/reference tracking through `vlv_iosf_sb_get/put()`.

### Dependencies

It includes Linux bit/type helpers plus `vlv_iosf_sb.h` and `vlv_iosf_sb_reg.h` for unit IDs and access functions. DPIO functions also depend on `enum dpio_phy`.

### Integration points

`vlv_dsi.c` uses FLISDSI wrappers for bandgap/rcomp programming. `vlv_dsi_pll.c` uses CCK wrappers for VLV DSI PLL registers. `intel_dpio_phy.c` uses DPIO wrappers for PHY registers. PUNIT/BUNIT/CCU/NC wrappers support other VLV/CHV display power and clock paths.

### Risks

Get/put mismatches can leave sideband units locked or unprotected. The non-i915 DPIO stub signature uses `int phy`, so callers should rely on normal i915 builds for type checking. Sideband reads/writes are low-level hardware operations with little validation.

### Test signals

Static build coverage, lockdep around IOSF get/put users, DSI PLL lock on CCK access, DSI bandgap programming through FLISDSI, and DPIO PHY programming success on VLV/CHV.
