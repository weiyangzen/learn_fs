# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline.c

Purpose: manages generic Komeda pipeline/component allocation, lookup, assembly, input/output capability verification, slave-pipeline discovery, and register/debug dumps.

Important APIs/types/functions: `komeda_pipeline_add()`, `komeda_pipeline_destroy()`, `komeda_pipeline_get_component()`, `komeda_pipeline_get_first_component()`, `komeda_component_add()`, `komeda_component_destroy()`, `komeda_pipeline_get_slave()`, `komeda_assemble_pipelines()`, `komeda_pipeline_dump()`, and `komeda_pipeline_dump_register()`.

Control flow: chip enumeration adds pipelines and components. Assembly verifies that advertised inputs resolve to existing components, fills reverse supported-output masks, finds right-side layers for layer split, and disables dual-link if hardware timing controller does not support it. KMS setup uses slave discovery to map CRTCs. Debug paths dump component capabilities and registers.

State and persistence: `komeda_pipeline` stores component pointers, availability masks, layer/scaler counts, DT graph nodes, dual-link flag, and chip funcs. Component structures store capabilities, IDs, MMIO bases, and function tables.

Dependencies/integration: OF node lifecycle, Linux clocks, seq_file, DRM logging, Komeda device/KMS/pipeline headers, and chip-specific component creation.

Risks: component IDs encode array positions and cross-pipeline resources, so wrong IDs miswire pipelines. `komeda_component_add()` requires layers/scalers in sequence. Destroy assumes component masks are valid and clocks/nodes were acquired. Test signals: resource enumeration logs, DT dual-link fallback, layer split right-layer selection, debugfs register dumps, and component graph consistency checks.
