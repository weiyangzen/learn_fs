## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.h

Purpose: public constructor declaration for the DCE11 underlay OPP wrapper.

Important API: `dce110_opp_v_construct(struct dce110_opp *opp110, struct dc_context *ctx)`. The header includes `dc_types.h`, `opp.h`, and `core_types.h`, exposing the object shape needed by resource construction.

Control flow and state: no runtime behavior is implemented here. It exists to allow resource code to instantiate the video OPP and receive a generic `opp` interface through `opp110->base`.

Risks and test signals: the header has no internal guards beyond include guards. The important tests are compilation of users that include it and runtime validation that the constructed OPP vtable is compatible with underlay display paths.
