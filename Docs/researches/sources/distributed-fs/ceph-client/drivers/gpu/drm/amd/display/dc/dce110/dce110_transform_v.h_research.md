## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.h

Purpose: public declarations for the DCE11 underlay transform plus its CSC/regamma helper entry points.

Important APIs and constants: `LB_TOTAL_NUMBER_OF_ENTRIES` is 1712, `LB_BITS_PER_ENTRY` is 144, `dce110_transform_v_construct`, `dce110_opp_v_set_csc_default`, `dce110_opp_v_set_csc_adjustment`, `dce110_opp_program_regamma_pwl_v`, `dce110_opp_power_on_regamma_lut_v`, and `dce110_opp_set_regamma_mode_v`.

Integration: the transform implementation uses this header to share CSC/regamma functions across files, and resource code uses the constructor to create the underlay transform object.

Risks and test signals: the header couples transform and OPP color-management APIs, so signature drift breaks multiple files. Build tests and underlay color/scaler runtime tests validate the contract.
