<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream.c

Purpose: Converts user-provided PowerVR command streams into firmware command structures using declarative stream definitions and feature/quirk gating.

Important APIs/types/functions: Public functions are `pvr_stream_process()` and `pvr_stream_create_musthave_masks()`. Important helpers include `stream_def_is_supported()`, `pvr_stream_get_data()`, `pvr_stream_process_1()`, and `pvr_stream_process_ext_stream()`.

Control flow: `pvr_stream_process()` validates a non-empty stream, reads a main-stream byte length and reserved padding word, decodes the main stream into `dest_out`, then optionally walks extension headers. Extension processing validates header type and valid-mask bits, verifies required UAPI quirks are present, decodes selected extension substreams, and checks that device-specific "must have" masks were satisfied.

State and persistence behavior: The main persistent state affected is the destination firmware command structure supplied by the caller. `pvr_stream_create_musthave_masks()` initializes `pvr_dev->stream_musthave_quirks` based on detected UAPI quirks 47217 and 49927.

Dependencies: Uses `struct pvr_device`, `pvr_device_has_feature()`, `pvr_device_has_uapi_quirk()`, firmware stream header masks from `pvr_rogue_fwif_stream.h`, and UAPI command stream definitions from `pvr_drm.h`.

Integration points: Job submission and context creation paths call this decoder with definitions from `pvr_stream_defs.c` to build `rogue_fwif_cmd_*` and static context-state structures passed to firmware.

Risks: Stream alignment is implicit and type-size dependent; wrong definitions or missed feature gating can desynchronize the stream and populate firmware registers with wrong values. Extension headers are attack surface from userspace, so bounds, masks, continuation handling, and must-have quirk validation are critical.

Test signals: Negative tests with truncated streams, non-zero padding, invalid extension headers, unsupported quirk bits, and missing must-have extensions; positive job submission on GPUs with and without gated features and UAPI quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream.c -->
