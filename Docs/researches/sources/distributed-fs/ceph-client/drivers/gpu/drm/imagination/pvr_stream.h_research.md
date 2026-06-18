<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream.h

Purpose: Declares the PowerVR stream decoder data model and public decoder entry points.

Important APIs/types/functions: Defines `enum pvr_stream_type`, `enum pvr_stream_size`, `struct pvr_stream_def`, `struct pvr_stream_ext_def`, `struct pvr_stream_ext_header`, and `struct pvr_stream_cmd_defs`. Public functions are `pvr_stream_process()` and `pvr_stream_create_musthave_masks()`.

Control flow: No implementation flow; this header describes the tables that `pvr_stream.c` interprets.

State and persistence behavior: `struct pvr_stream_cmd_defs` ties a stream type to main stream definitions, extension definitions, and destination structure size. Feature gating is represented by `PVR_FEATURE_NONE` and the `PVR_FEATURE_NOT` bit convention.

Dependencies: Uses Linux bits, limits, and fixed-width types; forward-declares `struct pvr_device` and `struct pvr_job`.

Integration points: Included by stream definition tables, job/context submission paths, and the stream decoder implementation.

Risks: Changing enum values or structure fields affects every stream table and decoder interpretation. `PVR_FEATURE_NOT` shares the high bit of a feature id and must not collide with real feature identifiers.

Test signals: Build coverage of all stream definitions, command-stream decode tests, and ABI tests that confirm expected ordering/size of streamed fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream.h -->
