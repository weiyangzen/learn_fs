# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/gr.h

Purpose: defines R535 graphics context-buffer and ZCULL-related control payloads used by GSP-backed GR initialization and context promotion.

Important definitions: `NV2080_CTRL_INTERNAL_STATIC_KGR_GET_CONTEXT_BUFFERS_INFO` returns `NV2080_CTRL_INTERNAL_STATIC_GR_GET_CONTEXT_BUFFERS_INFO_PARAMS`, an array of `NV2080_CTRL_INTERNAL_ENGINE_CONTEXT_BUFFER_INFO` entries per GR engine. Engine-context property IDs identify main, preemption, spill, pagepool, betacb, RTV, GFXP, FECS, privilege maps, and related buffer categories. `NV2080_CTRL_GPU_PROMOTE_CTX_BUFFER_ID_*` maps those categories into promote-context buffer IDs. The header includes `fifo.h` for `NV2080_CTRL_GPU_PROMOTE_CTX_PARAMS`.

Control flow and state: GR code reads this information to size/align context buffers, then allocates memory and promotes them into RM channel contexts. ZCULL context buffer size/alignment is also derived from this data.

Dependencies and integration: consumed by R535/R570 GR implementations, FIFO context promotion, and MMU/VMM helpers for mapping context buffers.

Risks and tests: stale buffer IDs or size/alignment fields can produce invalid contexts, GR channel failures, or RC events during rendering. Tests should include GR initialization, context creation/destruction, workloads that require preemption/context switching, and ZCULL-dependent rendering.
