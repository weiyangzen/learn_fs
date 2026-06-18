# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device_info.c

Purpose: maps firmware-provided feature, quirk, and enhancement bitmasks into fields inside `struct pvr_device`.

Important APIs/functions: `pvr_device_info_set_quirks()` maps `PVR_FW_HAS_BRN_*` bits to `pvr_dev->quirks.has_brn*`. `pvr_device_info_set_enhancements()` maps `PVR_FW_HAS_ERN_*` bits. `pvr_device_info_set_features()` maps `PVR_FW_HAS_FEATURE_*` bits to feature presence booleans and, where applicable, feature value fields. `pvr_device_info_set_common()` handles shared quirk/enhancement bitmask parsing and unsupported-bit warnings.

Control flow and state: mapping arrays store `offsetof()` values into `struct pvr_device`, allowing generic bit iteration to set booleans or values. Feature values are read sequentially from the parameter area after the feature bitmask; if a present valued feature lacks a parameter, `-EINVAL` is returned.

Dependencies and integration: depends on firmware device-info ABI constants, DRM warnings, `pvr_device` layout, and feature/quirk/enhancement structs.

Risks: offset mappings must stay synchronized with firmware enum maxima; `BUILD_BUG_ON` catches array-size drift. Unsupported bits warn but do not fail except malformed feature parameter streams. Reordering valued features changes parameter consumption semantics.

Test signals: firmware validation should populate expected feature fields; KUnit or firmware fixture tests should exercise unsupported bits and truncated feature-parameter streams.
