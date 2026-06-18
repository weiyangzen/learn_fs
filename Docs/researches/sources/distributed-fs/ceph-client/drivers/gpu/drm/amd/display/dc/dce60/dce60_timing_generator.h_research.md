## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.h

Purpose: public constructor declaration for the DCE6 timing-generator adapter.

Important API: `dce60_timing_generator_construct(struct dce110_timing_generator *tg, struct dc_context *ctx, uint32_t instance, const struct dce110_timing_generator_offsets *offsets)`.

Integration: the header documents that DCE6 inherits from DCE11. Resource code passes a DCE110-style object and offsets, and the implementation installs the DCE60 vtable.

Risks and test signals: include-order dependencies are possible because this header references `struct dce110_timing_generator` without including its header. Build coverage through resource construction is the main check.
