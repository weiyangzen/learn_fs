## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.c

Purpose: minimal constructor for the DCE11 video/underlay OPP object. It wires an underlay OPP to the generic DCE110 OPP operations for dynamic expansion, formatting, bit-depth reduction, and destroy.

Important API: `dce110_opp_v_construct(struct dce110_opp *opp110, struct dc_context *ctx)`. Its static `opp_funcs` table references `dce110_opp_set_dyn_expansion`, `dce110_opp_destroy`, `dce110_opp_program_fmt`, and `dce110_opp_program_bit_depth_reduction` from the shared DCE OPP implementation.

Control flow and state: construction stores the function table and context in `opp110->base`. No hardware registers are written here; later OPP calls perform the hardware programming. Dependencies include `dce/dce_opp.h`, DC context types, and DCE11 register headers.

Risks and test signals: this file has little logic, so risk is primarily integration mismatch: the underlay path may need different OPP behavior than the generic DCE110 callbacks provide. Build/link tests catch missing symbols; runtime modeset tests catch format and bit-depth callback compatibility.
