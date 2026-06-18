## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.h

Purpose: DCE120 timing-generator constructor declaration.

Important API: `dce120_timing_generator_construct(struct dce110_timing_generator *tg110, struct dc_context *ctx, uint32_t instance, const struct dce110_timing_generator_offsets *offsets)`. It includes the generic timing-generator interface, graphics object ids, and the DCE110 timing-generator base type.

Integration: DCE120 reuses the DCE110 container structure while substituting its SOC15-aware vtable and limits in the implementation.

Risks and test signals: compatibility depends on the shared DCE110 structure retaining fields needed by DCE120. Build coverage and runtime construction of each CRTC instance validate the interface.
