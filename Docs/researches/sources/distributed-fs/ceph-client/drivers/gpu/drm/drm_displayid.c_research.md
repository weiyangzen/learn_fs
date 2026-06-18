# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_displayid.c

Purpose: Implements iteration over DisplayID data blocks embedded in EDID extension blocks. It validates DisplayID section headers/checksums, applies monitor-specific quirks, walks all DisplayID extensions, and exposes base-section version and primary-use/product-type values.

Important APIs/types/functions: Internal/public-to-DRM functions include `displayid_iter_edid_begin`, `__displayid_iter_next`, `displayid_iter_end`, `displayid_version`, and `displayid_primary_use`. Static helpers are `get_quirks`, `displayid_get_header`, `validate_displayid`, `find_next_displayid_extension`, and `displayid_iter_block`. Main types are `struct displayid_iter`, `struct displayid_header`, `struct displayid_block`, and quirk descriptors keyed by `struct drm_edid_ident`.

Control flow: Iterator begin clears the iterator, stores the DRM EDID pointer, and records quirks. `__displayid_iter_next` first advances within the current section by the previous block header plus payload length; if no next block is valid, it searches for the next EDID extension with `DISPLAYID_EXT`, validates section length and checksum, records base-section version and primary-use from the first section, skips the DisplayID header, and returns the first valid data block. On exhaustion or invalid extension, it clears `drm_edid` so further calls return NULL. `displayid_iter_end` zeros the iterator.

State and persistence behavior: Iteration state is fully contained in caller-provided `struct displayid_iter`: current EDID, section pointer, section length, byte index, extension index, base version, primary-use/product-type, and quirks. No allocations or persistent state are used. Returned block pointers reference the original EDID data.

Dependencies and integration points: Integrates with DRM EDID helpers `drm_edid_find_extension` and `drm_edid_match`, DisplayID structures/constants from `drm_displayid_internal.h`, and DRM logging for checksum notes. EDID parsers use this iterator to find detailed timing, tiled display, vendor-specific, CTA, and other DisplayID blocks.

Risks: Invalid checksum causes the whole extension to be skipped unless a quirk says to ignore it. `find_next_displayid_extension` sets length to `EDID_LENGTH - 1` because the EDID extension checksum is outside DisplayID payload, so off-by-one mistakes would truncate or overrun parsing. The iterator stops on malformed current-block state with `WARN_ON`, which prevents continuing into later extensions. Base-section version/primary-use come from the first DisplayID section encountered.

Test signals: EDIDs with no DisplayID extension, one valid extension with multiple blocks, multiple DisplayID extensions, truncated headers, blocks whose payload exceeds section length, invalid checksums with and without the CSO quirk, base-section version/primary-use capture, iterator end/reset behavior, and consumers using `displayid_iter_for_each` over all block types.
