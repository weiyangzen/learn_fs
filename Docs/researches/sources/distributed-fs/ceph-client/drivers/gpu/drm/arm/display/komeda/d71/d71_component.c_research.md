# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_component.c

Purpose: implements D71-family hardware component discovery, validation, register programming, disable paths, and debug dumps for Komeda pipeline components.

Important APIs/types/functions: externally visible `d71_probe_block()`, `d71_dump()`, and `d71_pipeline_funcs`. Internal component handlers include layer, writeback layer, compositor, scaler, splitter, merger, image processor, and timing controller init/update/disable/dump functions. `get_resources_id()` maps D71 block IDs to Komeda component IDs; `d71_downscaling_clk_check()` enforces D71 scaler timing constraints.

Control flow: resource enumeration reads each block header and calls `d71_probe_block()`. For recognized block types it stores LPU/CU/DOU base addresses or creates Komeda components with chip-specific function tables. During atomic commit, generic pipeline update calls each active component `update()` to write framebuffer addresses, AFBC controls, input IDs, scaler phases, composition inputs, color/gamma/CTM coefficients, timing registers, and enable bits. Disable clears enable bits and input IDs.

State and persistence: persistent state is hardware register programming and component capability fields such as line sizes, ranges, supported rotations, supported color formats/depths, and split/merge limits. No software cache is maintained beyond DRM private states passed into update functions.

Dependencies/integration: depends on D71 register macros, Komeda pipeline/KMS/framebuffer/color types, `malidp_io`, DRM format/rotation/blending/color APIs, and seq_file debugfs dumps.

Risks: register offset arithmetic is dense and hardware-specific. Split/scaler phase math and AFBC payload/end-address selection are high-risk. Some init failures return `-1` instead of errno. Masked writes rely on callers passing values already limited to masks. Test signals: atomic modeset and plane-update tests, AFBC/non-AFBC framebuffer scanout, YUV color conversion, writeback jobs, split scaling, dual-link timing, downscaling clock rejection, IRQ error injection, and debugfs register dump review.
