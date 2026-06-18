# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline.h

Purpose: defines the generic Komeda pipeline/component model, per-component atomic state structures, data-flow configuration, chip pipeline callbacks, and pipeline/component APIs.

Important APIs/types/functions: component IDs/masks; `struct komeda_component_funcs`; base `komeda_component` and derived layer/scaler/compiz/merger/splitter/improc/timing structs and states; `struct komeda_data_flow_cfg`; `struct komeda_pipeline_funcs`; `struct komeda_pipeline` and `struct komeda_pipeline_state`; conversion macros and public builder/update/disable APIs.

Control flow: plane/wb/CRTC atomic checks construct `komeda_data_flow_cfg`, acquire private states for components, and fill component-specific state. Commit code later calls `komeda_pipeline_update()` or `komeda_pipeline_disable()` to dispatch chip callbacks.

State and persistence: distinguishes static hardware capabilities in component structs from transient atomic private states. Pipeline state tracks CRTC ownership and active component mask; component states track binding user, active/changed/affected inputs, and component-specific register data.

Dependencies/integration: DRM atomic helpers, Mali range utilities, color management, framebuffer/KMS forward declarations, and chip backends.

Risks: active/changed/affected input masks are subtle and must stay consistent for incremental register updates. Maximum input/layer/scaler constants cap hardware support. Test signals: atomic private state duplicate/reset behavior, resource contention across CRTCs, component changed-input updates, split/merge flows, and compile checks for all conversion macros.
