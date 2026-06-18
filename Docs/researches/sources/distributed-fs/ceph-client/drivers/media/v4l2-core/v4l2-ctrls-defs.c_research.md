# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-defs.c

## Purpose
This file centralizes standard V4L2 control metadata. It maps control IDs to menu label tables, integer-menu value tables, human-readable names, default type/range/step/default values, and standard control flags. The constructors in `v4l2-ctrls-core.c` use it to build standard controls without each driver duplicating metadata.

## Important APIs, types, and functions
`v4l2_ctrl_get_menu(u32 id)` returns a static NULL-terminated string table for menu controls such as MPEG audio/video options, camera exposure modes, color effects, H.264/HEVC/AV1 profiles and levels, flash modes, digital-video ranges, detection modes, and camera orientation. Empty strings in returned menus represent unsupported entries that query/validation code must skip.

`v4l2_ctrl_get_int_menu(u32 id, u32 *len)` returns static `s64` value arrays for integer-menu controls, currently VPX partition and reference-frame counts, and reports the table length. `v4l2_ctrl_get_name(u32 id)` maps a broad set of user, codec, camera, FM radio, flash, JPEG, image source/processing, DV, tuner, detection, stateless codec, and colorimetry control IDs to stable display names. `v4l2_ctrl_fill()` derives the default `enum v4l2_ctrl_type`, range, step, default value, and flags for a control ID.

## Control flow
All exported functions are switch-based metadata lookups. Standard control construction typically calls `v4l2_ctrl_fill()` first. That function initializes `name` from `v4l2_ctrl_get_name()`, clears flags, classifies IDs by type, applies special ranges/defaults for controls that need them, then applies secondary flag classifications such as `UPDATE`, `SLIDER`, `READ_ONLY`, `WRITE_ONLY`, `EXECUTE_ON_WRITE`, `VOLATILE`, `MODIFY_LAYOUT`, and `DYNAMIC_ARRAY`.

Menu constructors then call `v4l2_ctrl_get_menu()` or `v4l2_ctrl_get_int_menu()` to obtain the legal options. Query-menu and validation paths in the API/core files later use the returned tables, skip masks, and default range information to accept or reject userspace indices.

## State and persistence behavior
This file stores no mutable runtime state. All menus and integer menus are function-local static constant arrays. The outputs are metadata pointers and scalar values consumed by control allocation. Because the returned pointers refer to static storage, callers must not modify them and do not own their lifetime.

## Dependencies and integration points
It depends on `media/v4l2-ctrls.h` for all control IDs, types, flags, and constants. It is used by `v4l2-ctrls-core.c` constructors and indirectly by `v4l2-ctrls-api.c` query and validation paths. It must stay aligned with public UAPI definitions in `videodev2.h` and `v4l2-controls.h`; comments explicitly require case ordering to match those headers in several switch blocks.

## Risks
The main risk is metadata drift. If a new UAPI control is added without a matching name/type/range/menu entry, standard constructors may create an integer control by default or fail later. Wrong type classification can expose the wrong ABI shape. Wrong ranges or defaults can reject valid applications or permit invalid hardware settings. Menu arrays must remain ordered to match enum values; inserting or reordering labels breaks userspace-visible meaning. Dynamic-array flags for stateless codec controls must match the payload semantics expected by request and validation code.

## Test signals
Coverage should verify that every standard control ID in the supported headers has the expected name, type, min/max/step/default, flags, and menu table where applicable. Menu tests should check NULL termination, skipped or empty entries, integer-menu lengths, and constructor rejection when a standard menu is missing. ABI regression tests should compare known control metadata for representative user, camera, codec, stateless codec, and DV controls.
