## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.h

Purpose: public constructor declaration for the DCE11 underlay/video timing generator.

Important API: `dce110_timing_generator_v_construct(struct dce110_timing_generator *tg110, struct dc_context *ctx)`. The header depends on the caller having the shared DCE110 timing-generator type visible.

Control flow and state: no local logic. Construction assigns the underlay controller id and underlay callback table in the implementation.

Risks and test signals: because the header omits direct includes for the involved types, include-order dependencies can surface if it is used outside existing resource code. Build tests around resource construction are the main signal.
