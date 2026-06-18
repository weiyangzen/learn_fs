<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.c

Purpose: implements Register Table Processing (RTP), a rule/action engine used to apply platform, IP-version, stepping, GT, and engine-class specific register programming or active workaround tracking.

Important APIs and control flow: `rule_matches()` evaluates AND groups separated by `XE_RTP_MATCH_OR`, supports platform/subplatform, platform/graphics/media stepping, graphics/media version ranges, integrated/discrete, engine class/not-class, and callback rules. `xe_rtp_process_to_sr()` turns matching `xe_rtp_entry_sr` actions into `xe_reg_sr` entries, optionally iterating every engine and optionally skipping SR-IOV VF devices. `xe_rtp_process()` evaluates actionless entries for active tracking. `xe_rtp_process_ctx_enable_active_tracking()` registers a bitmap that matching entries set.

State and dependencies: context can be device, GT, or engine, selected by `XE_RTP_PROCESS_CTX_INITIALIZER`. Actions may be engine-base relative. Dependencies include register SR, GT topology, configfs PSMI, SR-IOV mode, and device platform metadata.

Risks and test signals: rule macros allow compound static tables, so KUnit should validate OR behavior, empty/invalid rule warnings, media-versus-graphics GT filtering on standalone media platforms, active bitmap bounds, engine-base offset application, and VF skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.c -->
