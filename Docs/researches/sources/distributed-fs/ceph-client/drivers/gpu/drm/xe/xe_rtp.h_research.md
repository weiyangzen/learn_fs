<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.h

Purpose: provides the public macro DSL and function declarations for RTP tables.

Important APIs and macros: rule macros encode platform, subplatform, stepping, graphics/media version/range/any-GT, integrated/discrete, engine class, callback, and OR conditions. Action macros encode full writes, set/clear, field-set with or without read masks, and whitelist actions. `XE_RTP_RULES()` and `XE_RTP_ACTIONS()` build compound literal arrays, up to 12 items. `XE_RTP_PROCESS_CTX_INITIALIZER()` uses `_Generic` to infer device/GT/engine context.

Integration points: used by workaround and whitelist tables throughout Xe to populate `xe_reg_sr` tables or active workaround bitmaps. Declares match helpers for even engine instance, first render/compute, non-VF, PSMI enabled, discontiguous DSS groups, and FlatCCS.

Risks and test signals: macro expansion mistakes are compile-time hard to diagnose. Tests should compile representative tables for all rule/action forms and verify read masks, engine-base flags, and OR semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.h -->
