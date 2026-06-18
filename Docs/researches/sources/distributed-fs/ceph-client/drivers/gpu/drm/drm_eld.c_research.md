# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_eld.c

## Purpose

`drm_eld.c` provides small exported helpers for reading and writing Short Audio Descriptors inside an ELD buffer. ELD is the EDID-like data structure passed from graphics drivers to HDMI/DP audio code. These helpers convert between the packed three-byte CTA SAD representation stored in ELD and the structured `struct cea_sad` representation used by DRM EDID helpers.

## Important APIs

`drm_eld_sad_get(const u8 *eld, int sad_index, struct cea_sad *cta_sad)` validates that `sad_index` is within `drm_eld_sad_count(eld)`, computes the SAD address with `DRM_ELD_CEA_SAD(drm_eld_mnl(eld), sad_index)`, and decodes the three bytes through `drm_edid_cta_sad_set()`. `drm_eld_sad_set(u8 *eld, int sad_index, const struct cea_sad *cta_sad)` performs the inverse operation with `drm_edid_cta_sad_get()`. Both return `0` on success and `-EINVAL` when the requested index is out of range. Both functions are exported.

## Control Flow

The helpers are deliberately direct. They trust the caller to provide a valid ELD buffer, derive the monitor-name length with `drm_eld_mnl()`, use that value to locate the SAD array, then copy/translate one SAD. No allocation, iteration, or locking is performed here.

## State and Persistence Behavior

`drm_eld_sad_get()` is read-only with respect to the ELD buffer and writes only the caller's destination `struct cea_sad`. `drm_eld_sad_set()` mutates exactly three bytes in the caller-provided ELD buffer. There is no persistent state in this file. Connector-level locking, when needed, is the caller's responsibility; `drm_edid.c` builds ELD under `connector->eld_mutex`, but these standalone helpers do not take that mutex.

## Dependencies and Integration Points

The file depends on `drm_eld.h` for ELD layout helpers and `drm_edid.h` for `struct cea_sad` conversion helpers. Its integration point is audio capability manipulation by DRM and HDMI/DP audio drivers after ELD has been built by EDID parsing.

## Risks and Edge Cases

Only the upper bound is checked; negative `sad_index` values are not explicitly rejected before pointer arithmetic. Callers should avoid negative indexes. The helpers also assume `eld` points to a well-formed buffer large enough for its advertised monitor-name length and SAD count. If those fields are corrupt, the computed offset can be wrong. Since no locks are taken, concurrent readers/writers of the same connector ELD need external serialization.

## Test Signals

Unit tests should construct ELD buffers with different monitor-name lengths and SAD counts, verify that each valid index round-trips through `drm_eld_sad_get()` and `drm_eld_sad_set()`, and verify `-EINVAL` for indexes equal to or above the SAD count. Negative-index behavior should be treated as a caller-contract hazard. Integration tests can compare SADs parsed from EDID with SADs later read from the generated connector ELD.
