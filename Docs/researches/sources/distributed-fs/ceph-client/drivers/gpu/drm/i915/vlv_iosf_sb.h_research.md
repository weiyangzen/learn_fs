# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb.h

Purpose: declares the VLV/CHV IOSF sideband unit enumeration and access API.

Important APIs/types: `enum vlv_iosf_sb_unit` names BUNIT, CCK, CCU, DPIO, DPIO_2, FLISDSI, GPIO, NC, and PUNIT. Public functions are init/fini, get/put, and read/write.

Control flow and state: callers initialize per-device sideband state, acquire a unit mask, perform read/write operations, then release the same unit mask.

Dependencies and integration: includes `vlv_iosf_sb_reg.h` so consumers can use sideband register constants. Implementation relies on `drm_i915_private` sideband lock/QoS fields.

Risks: enum values are used as bit indices in `unit_mask`; reordering or inserting values affects mask users.

Test signals: compile coverage from platform-specific VLV/CHV code and runtime warnings for invalid or unbalanced unit access.
