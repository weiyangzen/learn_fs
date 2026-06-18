<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_types.h

Purpose: defines RTP actions, rules, entries, match types, and processing context.

Important types: `struct xe_rtp_action` stores register, clear/set/read masks, and flags such as `XE_RTP_ACTION_FLAG_ENGINE_BASE`; `struct xe_rtp_rule` stores a match type and union payload for platform, version, stepping, engine class, or callback; `struct xe_rtp_entry_sr` combines named rules/actions and flags such as `FOREACH_ENGINE`; `struct xe_rtp_entry` is actionless; `struct xe_rtp_process_ctx` identifies device/GT/engine context and optional active-entry bitmap.

Risks and test signals: `u8` counters cap table size and rule/action counts. Tests should confirm entries with 12 macro arguments fit and that active bitmap sizes match `n_entries`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_types.h -->
