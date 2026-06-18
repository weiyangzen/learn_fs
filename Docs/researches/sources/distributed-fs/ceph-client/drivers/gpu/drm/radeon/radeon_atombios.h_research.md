# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atombios.h

Purpose: declares the small private AtomBIOS display-facing interface shared by Radeon driver compilation units.

Important APIs/types/functions: forward-declares `drm_connector`, `drm_device`, `drm_display_mode`, `radeon_device`, and `radeon_encoder`. Exposes `radeon_atom_get_tv_timings` for analog TV mode timing extraction, `radeon_add_atom_encoder` for creating AtomBIOS-backed encoders, and `radeon_atom_backlight_init` for AtomBIOS panel backlight setup.

Control flow: this header has no runtime control flow. It defines compile-time linkage between AtomBIOS implementation code and callers in the Radeon display stack.

State and persistence: no state is stored here. The declared functions operate on runtime DRM/Radeon objects supplied by callers.

Dependencies and integration: guarded by `__RADEON_ATOMBIOS_H__`. Included by AtomBIOS and display encoder/backlight code that needs the private prototypes without importing full struct definitions.

Risks: prototype drift against implementation or caller expectations would break builds or produce ABI mismatches inside the kernel module. Because the declarations use forward types, callers still need the right full definitions before dereferencing objects.

Test signals: normal Radeon kernel build coverage, especially compilation units that include this header and call TV timing, encoder creation, or backlight initialization helpers.
