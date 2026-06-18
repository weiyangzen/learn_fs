# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_edid_load.c

## Purpose

`drm_edid_load.c` implements firmware-backed EDID override loading for DRM connectors. It lets the `drm.edid_firmware` module parameter bypass physical monitor probing and supply an EDID blob from `/lib/firmware`. This is used for broken displays, missing DDC paths, reproducible testing, and forced mode discovery.

## Important APIs and Data

The file owns the static `edid_firmware[PATH_MAX]` module parameter. The exported entry point within DRM core is `drm_edid_load_firmware(struct drm_connector *connector)`, declared through internal headers and called by `drm_edid.c` when fetching connector overrides. The local helper `edid_load()` uses `request_firmware()`, wraps the returned bytes with `drm_edid_alloc()`, validates the result with `drm_edid_valid()`, frees invalid wrappers, releases firmware with `release_firmware()`, and returns either a valid `const struct drm_edid *` or an `ERR_PTR()`.

The module parameter accepts comma-separated entries. Entries may be connector-specific using `CONNECTOR_NAME:path`, or generic fallback paths without a connector prefix.

## Control Flow

`drm_edid_load_firmware()` first returns `-ENOENT` if the module parameter is empty. It duplicates the parameter string with `kstrdup()` so it can destructively parse it with `strsep()`. For each comma-separated item, it checks for a colon. If a colon exists, the prefix is compared with `connector->name`; a match selects the substring after the colon and stops parsing. If no colon exists and the item is non-empty, it becomes the current fallback, with the last generic entry winning. If the loop reaches the end without a connector-specific match, it uses the fallback if present or returns `-ENOENT`.

Before loading, a trailing newline is stripped from the selected firmware name. `edid_load()` then requests the firmware against `connector->dev->dev`, logs failure with connector id/name and errno, duplicates firmware data into a DRM EDID wrapper, validates the EDID against size and block checksums, and reports invalid blobs as `-EINVAL`. The temporary parameter copy is freed before returning.

## State and Persistence Behavior

The only persistent state is the module parameter buffer. Returned EDID wrappers are freshly allocated and owned by the caller, which must call `drm_edid_free()`. Firmware contents are not cached by this file after `release_firmware()`. Because connector matching is based on the current `connector->name`, stable connector naming is part of the behavior.

## Dependencies and Integration Points

The file depends on Linux firmware loading, module parameter infrastructure, DRM connector/device logging, and EDID allocation/validation from `drm_edid.c`. Its primary integration point is `drm_edid_override_get()` in `drm_edid.c`, where debugfs EDID override has priority and firmware EDID is the fallback override source. Drivers do not usually call this file directly.

## Risks and Edge Cases

The string parser intentionally tolerates multiple commas by ignoring empty fallback entries. Connector-specific matching uses `strncmp(connector->name, edidname, colon - edidname)`, so correctness depends on the prefix length and connector names; malformed prefixes that are partial connector names can be risky if not matched carefully by callers' naming expectations. The selected name assumes a non-empty string before trimming the last character; empty items are filtered for fallback but connector-specific empty paths after a colon could still produce an invalid firmware request. Invalid firmware contents are rejected by `drm_edid_valid()`, so incorrectly sized or checksum-bad blobs fail rather than propagating to connector state.

## Test Signals

Tests should cover an empty parameter, one generic firmware path, multiple generic paths with last fallback winning, connector-specific entries before and after fallbacks, trailing newline trimming, missing firmware, invalid EDID firmware, and valid multi-block EDID firmware. Integration tests should verify that firmware EDID is used when DDC probing fails or is bypassed by override logic, and that debug logs identify the connector and firmware path on failures.
