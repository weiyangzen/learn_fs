# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_shading.c

Purpose: `sh_css_param_shading.c` allocates, frees, generates, crops, and interpolates lens shading correction tables. It prepares sensor-space shading data for the grid dimensions and padding requirements of a selected ISP binary.

Important APIs/types/functions: internal `crop_and_interpolate()` performs bilinear interpolation from an input shading table to an output table while accounting for cropped target dimensions and left/right/top padding. `sh_css_params_shading_id_table_generate()` creates an identity shading table filled with 1s and zero fraction bits. `prepare_shading_table()` chooses identity output when input is absent or crops/interpolates an input table for a binary, BDS factor, sensor binning, and ISP padding. `ia_css_shading_table_alloc()` and `ia_css_shading_table_free()` manage table objects and per-color planes.

Control flow and state: interpolation computes source grid positions for each output color plane, clamps source indices at sensor/table edges, and calculates a weighted bilinear result. `prepare_shading_table()` derives input resolution from the binary, adjusts left/right/top padding for BDS and sensor binning, clips to input sensor dimensions, allocates the target table, and processes every `IA_CSS_SC_NUM_COLORS` plane. There is no global state.

Dependencies and integration: it depends on shading public types, binary descriptors, BDS fraction helper `sh_css_bds_factor_get_fract()`, `sh_css_defs.h` sizing rules, and allocation/logging helpers. `sh_css_params.c` calls it in legacy shading conversion mode and stores the resulting table to DDR.

Risks: the interpolation math is sensitive to zero or one table dimensions because it divides by `width - 1` and `height - 1`. Padding arithmetic mixes signed and unsigned values; negative right padding is accepted as an `int` and later contributes to padded width. Legacy conversion mode can allocate temporary tables repeatedly. Identity table generation does not set sensor dimensions, which is fine for ISP identity use but may surprise callers inspecting metadata.

Test signals: tests should cover identity generation, null input fallback, all four color planes, padding cases described in the comment, BDS factors, sensor binning shifts, small table dimensions, edge clamping, and allocation failure cleanup. Golden-image or table-golden tests are especially useful for interpolation correctness.
