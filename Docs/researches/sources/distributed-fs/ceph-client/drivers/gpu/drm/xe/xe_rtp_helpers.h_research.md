<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_helpers.h

Purpose: contains private preprocessor helpers used only by `xe_rtp.h` to build the RTP macro DSL.

Important macros: `XE_RTP_PASTE_FOREACH()` pastes a prefix onto tuple elements and joins them with a configured separator for 1 to 12 arguments. `XE_RTP_DROP_CAST()` removes a cast wrapper from compound register macros so register initializers can be embedded in action literals.

Dependencies and risks: guarded by `_XE_RTP_INCLUDE_PRIVATE_HELPERS` so it is not included directly. Changes can silently alter many RTP tables, so tests should inspect preprocessed expansion for representative rule and action macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_helpers.h -->
