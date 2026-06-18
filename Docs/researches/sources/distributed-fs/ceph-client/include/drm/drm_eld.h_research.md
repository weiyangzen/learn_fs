# sources/distributed-fs/ceph-client/include/drm/drm_eld.h

Purpose: Defines HDMI/DisplayPort ELD byte offsets, masks, and helpers for extracting or updating monitor audio capability information derived from EDID.

Important APIs, types, and functions: Defines ELD header and baseline block offsets/masks for version, baseline length, CEA EDID version, monitor name length, SAD count, connector type, AI/HDCP support, audio sync delay, speaker allocation, port ID, manufacturer/product IDs, monitor name, and SAD array offsets. Helpers include `drm_eld_mnl()`, `drm_eld_sad_get()`, `drm_eld_sad_set()`, `drm_eld_sad()`, `drm_eld_sad_count()`, `drm_eld_calc_baseline_block_size()`, `drm_eld_size()`, `drm_eld_get_spk_alloc()`, and `drm_eld_get_conn_type()`.

Control flow: Connector/audio code builds or reads an ELD buffer, sets monitor name and SAD data, computes the baseline length, and exposes the buffer to audio drivers. Consumers validate version and monitor-name length before returning the SAD pointer, then use count and size helpers to traverse the audio descriptors.

State and persistence: ELD is an in-memory byte buffer associated with connector/audio state. It persists only while connector state is cached; no on-disk storage exists. The byte layout is ABI-like because audio drivers and userspace diagnostics expect exact offsets.

Dependencies and integration points: Depends on `struct cea_sad` from EDID parsing and integrates with HDMI/DP audio, DRM connector EDID parsing, speaker allocation reporting, and codec/ALSA handoff paths.

Risks and test signals: Risks include out-of-bounds SAD access when monitor-name length or SAD count is corrupt, wrong baseline length units, connector-type bit misinterpretation, and accepting unsupported ELD versions. Test ELD buffers with HDMI and DP types, zero and maximum monitor-name lengths, multiple SADs, malformed version fields, speaker allocation masks, audio delay limits, and round-trip SAD get/set.
