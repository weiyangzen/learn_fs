# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline_state.c

Purpose: performs Komeda atomic resource allocation and data-flow validation for layers, scalers, splitters, mergers, compositors, image processors, timing controllers, writeback, and display output.

Important APIs/types/functions: exported `pipeline_composition_size()`, `komeda_complete_data_flow_cfg()`, layer/wb/display/split data-flow builders, `komeda_release_unclaimed_resources()`, `komeda_pipeline_disable()`, `komeda_pipeline_update()`, and `komeda_pipeline_get_old_state()`. Internal helpers allocate pipeline/component private states, bind users, validate dimensions/formats/scaling, split flows, and build component input chains.

Control flow: plane check initializes data flow, validates layer and optional scaler/split/merge, then feeds compiz. CRTC check validates slave/master compiz output, improc color/depth, and timing controller. Writeback builds `compiz -> scaler/splitter/merger -> wb_layer`. Release/unbound logic marks no-longer-used components for disable. Commit update iterates changed components and calls chip update/disable functions.

State and persistence: atomic private state records component users, inputs, per-component parameters, active component masks, and pipeline ownership. No persistent storage; committed state becomes current DRM private object state and hardware registers after flush.

Dependencies/integration: DRM atomic state locking, CRTC/plane/writeback state, Komeda framebuffer and format checks, scaler clock callback, color conversion, and chip component funcs.

Risks: resource allocation can return `-EBUSY` or `-EDEADLK` under contention. Split math handles rotation, reflection, YUV alignment, overlap, crops, and z-order and is high risk. `komeda_compiz_validate()` sets output before checking `dflow` non-NULL, though current callers pass non-NULL. Test signals: IGT atomic plane scaling/rotation/zpos, dual-pipeline composition, split-scaling edge cases, writeback scaling, resource release after plane disable, and modeset disable/enable cycles.
