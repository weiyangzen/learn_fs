# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_segment.c

This file implements internal LUKS2 JSON segment access, creation, flag handling, lookup, and comparison helpers.

Main responsibilities:
- Read segment fields: `offset`, `type`, `iv_tweak`, `size`, cipher `encryption`, `sector_size`, OPAL segment id/key size/size.
- Handle flags arrays, including backup detection via flags prefixed by `backup-`.
- Create `linear`, `crypt`, `hw-opal`, and `hw-opal-crypt` segment JSON objects.
- Add crypt fields: `iv_tweak`, `encryption`, `sector_size`, optional integrity object, optional `in-reencryption` flag.
- Find first/last segment by type, first unused id, segment by flag, and segment currently flagged `in-reencryption`.
- Set the whole `segments` object on a header, optionally committing it.
- Assign/remove segment flags and remove empty flag arrays.
- Compare key segment characteristics for compatibility.

Important functions:
- `json_segments_get_minimal_offset()` returns the smallest non-backup segment offset.
- `json_segment_is_backup()` treats any flag with prefix `backup-` as a backup segment.
- `json_segments_count()` counts only non-backup segments.
- `json_segment_create_crypt()` and `json_segment_create_linear()` are used heavily by reencryption.
- `LUKS2_get_segment_id_by_flag()` and `LUKS2_get_segment_by_flag()` are central to finding reencryption backup segments.
- `LUKS2_segments_dynamic_size()` detects non-backup segments with `"size": "dynamic"`.

OPAL support:
- `hw-opal` and `hw-opal-crypt` segment types carry `opal_segment_number`, `opal_key_size`, and `opal_segment_size`.
- Helper predicates distinguish OPAL-only, OPAL-crypt, and any OPAL segment.

Notable behavior:
- Missing cipher field defaults to `"null"` with a FIXME noting pseudo-null cipher handling should happen elsewhere.
- Invalid or missing sector size defaults to 512-byte sector size.
- Segment ids are string keys in JSON and are converted with `atoi()`.
- `LUKS2_segment_first_unused_id()` returns the current object length, so it assumes dense/append-style segment ids.

Dependencies:
- `luks2_internal.h`
- JSON-C
- LUKS2 array helpers
- crypt JSON uint helpers

This file is a foundational utility for LUKS2 metadata manipulation and is especially important for reencryption because backup segments are intentionally present in metadata but excluded from normal active segment counting.
