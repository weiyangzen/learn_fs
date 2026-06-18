# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_format_caps.c

Purpose: implements format/modifier capability lookup and plane format-list generation for Komeda layers.

Important APIs/types/functions: `komeda_get_format_caps()`, `komeda_get_afbc_format_bpp()`, `komeda_supported_modifiers[]`, `komeda_format_mod_supported()`, `komeda_get_layer_fourcc_list()`, and `komeda_put_fourcc_list()`.

Control flow: framebuffer creation and plane validation ask the format table for a fourcc/modifier match. For linear formats it selects caps with no AFBC layouts; for AFBC it verifies requested feature bits and layout against caps. Plane creation builds a de-duplicated fourcc list for a layer type. Format/mod support also calls optional chip-specific validation.

State and persistence: `komeda_supported_modifiers` is a global immutable list exposed to DRM plane initialization. Allocated fourcc lists are temporary and freed after plane init.

Dependencies/integration: depends on DRM fourcc/AFBC definitions, `malidp_utils`, D71 format table initialization, framebuffer creation, and plane funcs.

Risks: `has_bits(afbc_features, caps->supported_afbc_features)` allows subsets but rejects feature bits not advertised; correctness depends on caller expectations. Fourcc de-duplication uses a reverse loop with signed index. Modifier list is broad and filtered later by per-layer checks. Test signals: format/modifier enumeration with IGT, AFBC layout/feature combinations, per-layer supported formats, and framebuffer creation failure paths.
