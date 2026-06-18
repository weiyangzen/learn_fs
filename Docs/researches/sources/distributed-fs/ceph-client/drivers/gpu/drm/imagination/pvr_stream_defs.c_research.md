<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream_defs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream_defs.c

Purpose: Provides declarative field-order definitions for user command streams targeting Rogue firmware command and static context structures.

Important APIs/types/functions: Exports `pvr_cmd_geom_stream`, `pvr_cmd_frag_stream`, `pvr_cmd_compute_stream`, `pvr_cmd_transfer_stream`, `pvr_static_render_context_state_stream`, and `pvr_static_compute_context_state_stream`. Helper macros map firmware struct members to offsets, sizes, array sizes, and feature predicates.

Control flow: There is no runtime code beyond table initialization. The order of each `struct pvr_stream_def` array determines how `pvr_stream_process()` consumes aligned stream data.

State and persistence behavior: These tables define how userspace-controlled streams fill firmware-visible structures including `rogue_fwif_cmd_geom`, `rogue_fwif_cmd_frag`, `rogue_fwif_cmd_compute`, `rogue_fwif_cmd_transfer`, and static render/compute context switch state.

Dependencies: Relies on firmware interface structs from `pvr_rogue_fwif_client.h`, stream extension header masks from `pvr_rogue_fwif_stream.h`, feature IDs from `pvr_device_info.h`, and UAPI quirk ids.

Integration points: The job and context code passes these exported definitions to `pvr_stream_process()`. Extension definitions for BRN47217 and BRN49927 tie hardware errata quirks to additional required fields.

Risks: The source comment correctly notes that new parameters must be appended to preserve stream order. Reordering, missing feature predicates, or incorrect `offsetof()` target members would break userspace/kernel/firmware agreement.

Test signals: Decode known-good geometry, fragment, compute, transfer, and static context streams; test feature-present and feature-absent devices; test quirk paths for BRN47217/49927; compare generated firmware structures against userspace expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream_defs.c -->
