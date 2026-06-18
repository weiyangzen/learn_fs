# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_backlight.h

## Purpose
Declares the AUX backlight initializer used by the i915 display backlight code to install DisplayPort AUX backlight callbacks for an eDP connector.

## Important APIs, types, and functions
- Forward declares `struct intel_connector`.
- Exports `int intel_dp_aux_init_backlight_funcs(struct intel_connector *intel_connector);`.
- Uses a conventional include guard `__INTEL_DP_AUX_BACKLIGHT_H__`.

## Control flow
This header has no runtime control flow. It allows other display code, especially the backlight setup path, to call into `intel_dp_aux_backlight.c` without exposing Intel/VESA helper internals or the local module-parameter enum.

## State and persistence
No state is defined here. The declared initializer mutates connector panel backlight function pointers and state in the implementation file.

## Dependencies and integration points
Integrated by including it from `intel_dp_aux_backlight.c` and caller code such as `intel_backlight.c`. The narrow declaration keeps AUX backlight policy private to the implementation.

## Risks
The header is intentionally minimal. Any additional caller needing lower-level Intel or VESA helpers would require API expansion, which should be avoided unless there is a real shared use.

## Test signals
Build coverage is the primary signal. A missing or mismatched declaration would break callers at compile time.
