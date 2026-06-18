# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb_reg.h

Purpose: defines IOSF sideband register addresses and bit fields used by Valleyview/Cherryview display, power, PLL, frequency, and power-gate control code.

Important definitions: BUNIT register `BUNIT_REG_BISOC`; PUNIT media/display/ISP power state registers and `_SSPM*` masks; power gate control/status macros and indices; GPU frequency/fuse/duty-cycle registers; DDR frequency force bits; NC fuse fields; turbo SoC override bits; CCK HPLL/DSI PLL/control divider/clock fields.

Control flow and state: the header is pure constants and macros. State is hardware-resident in sideband registers accessed via `vlv_iosf_sb_read()`/`write()`.

Dependencies and integration: included by `vlv_iosf_sb.h` and platform code that needs symbolic register fields for PUNIT, CCK, BUNIT, or NC sideband accesses.

Risks: bit encodings are hardware contracts. Incorrect shifts/masks can break power-gating, PLL programming, display clocks, or GPU frequency detection. Several comments mark Cherryview-specific fields, so cross-platform users must choose fields carefully.

Test signals: validated indirectly by VLV/CHV display bring-up, power management, frequency initialization, suspend/resume, and sideband access smoke tests.
