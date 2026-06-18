## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_csc_v.c

Purpose: underlay color-space conversion programming for DCE11 color-management registers. It programs output CSC matrices, input CSC matrices, CSC mode selection, and denormalization/clamp behavior for graphics/video color spaces.

Important APIs: `dce110_opp_v_set_csc_default` and `dce110_opp_v_set_csc_adjustment`. Important data includes `global_color_matrix`, `input_csc_matrix`, `enum csc_color_mode`, and `enum grph_color_adjust_option`. `program_color_matrix_v` double-buffers output CSC register sets A/B, while `program_input_csc` does the same for input CSC.

Control flow: default setup optionally programs a software output matrix based on output color space, always programs input CSC from input color space, selects hardware/predefined/programmed output CSC mode, then sets denormalization based on output color depth. Adjustment setup writes a caller-provided matrix and selects software output CSC mode.

State and dependencies: all state is hardware register state under `COL_MAN_*`, `OUTPUT_CSC_*`, `INPUT_CSC_*`, and `DENORM_CLAMP_CONTROL`. Dependencies are DCE11 register headers, fixed register-field macros, and DC color-space/depth enums. Risks include unsupported SRGB limited underlay output returning false internally, TODO-marked matrix correctness for limited YCbCr, input type hard-coded to 8.4, and lack of validation on caller-provided matrices. Test signals are color-space conformance, limited/full RGB behavior, YCbCr601/709 conversion, and register A/B bank toggling without visible tearing.
