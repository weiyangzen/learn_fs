<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream_defs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream_defs.h

Purpose: Declares the exported PowerVR stream definition tables implemented by `pvr_stream_defs.c`.

Important APIs/types/functions: Extern declarations for the six `struct pvr_stream_cmd_defs` objects covering geometry, fragment, compute, transfer, static render context, and static compute context streams.

Control flow: No runtime flow.

State and persistence behavior: Provides access to immutable command-definition state used to decode user streams.

Dependencies: Includes `pvr_stream.h` for `struct pvr_stream_cmd_defs`.

Integration points: Included by callers that select a stream definition for `pvr_stream_process()`.

Risks: Missing an extern declaration prevents callers from using a new stream table. Renaming declarations without updating implementations or users breaks build-time linkage.

Test signals: Link/build coverage and runtime decode of every declared stream type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_stream_defs.h -->
