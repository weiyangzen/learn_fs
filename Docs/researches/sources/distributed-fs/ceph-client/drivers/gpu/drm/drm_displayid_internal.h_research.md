# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_displayid_internal.h

Purpose: Defines DRM-internal DisplayID constants, packed wire-format structures, and iterator declarations used by EDID/DisplayID parsing code.

Important APIs/types/functions: Defines VESA OUI, DisplayID 2.0 version, DisplayID 1.x and 2.0 data-block tags, product type and primary-use constants, packed structs `displayid_header`, `displayid_block`, `displayid_tiled_block`, `displayid_detailed_timings_1`, `displayid_detailed_timing_block`, `displayid_formula_timings_9`, `displayid_formula_timing_block`, and `displayid_vesa_vendor_specific_block`, bitfield masks `DISPLAYID_VESA_MSO_OVERLAP` and `DISPLAYID_VESA_MSO_MODE`, private iterator struct `displayid_iter`, iterator declarations, `displayid_iter_for_each`, `displayid_version`, and `displayid_primary_use`.

Control flow: There is no executable flow. The header maps DisplayID byte layouts into packed C structures and provides declarations for the iterator implemented in `drm_displayid.c`.

State and persistence behavior: No global state is stored. `struct displayid_iter` carries transient parse state over EDID memory supplied by callers. Packed structs are views over EDID/DisplayID binary data and should not be treated as independently owned storage.

Dependencies and integration points: Used by `drm_displayid.c` and EDID parsing paths that decode tiled display topology, detailed timings, formula timings, VESA vendor-specific MSO data, and CTA/vendor blocks. It depends only on Linux integer/bit headers and a forward declaration of `struct drm_edid`.

Risks: Packed struct definitions must exactly match the DisplayID specification; field-size mistakes propagate into EDID parsing and mode discovery. Multibyte fields are little-endian where declared and require correct conversion by consumers. The iterator is marked private and should not be accessed directly outside its helper API.

Test signals: Compile-time layout checks where available, parser tests using known DisplayID fixtures for each block type, tiled-topology EDIDs, detailed/formula timing EDIDs, VESA vendor-specific MSO data, DisplayID 1.x vs 2.0 tag handling, and endian-sensitive multibyte timing fields.
