# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/color/color_gamma.h

Purpose: Declares the color gamma/regamma public interface and several data structures used to pass user regamma ramps, coefficient forms, HDR tone-mapping parameters, and scratch buffers into color curve generation.

Important APIs and types: `union regamma_flags`, `struct regamma_ramp`, `struct regamma_coeff`, `struct regamma_lut`, `struct hdr_tm_params`, `struct calculate_buffer`, and `struct translate_from_linear_space_args`. Public functions are `setup_x_points_distribution`, `log_x_points_distribution`, `precompute_pq`, `precompute_de_pq`, `mod_color_calculate_regamma_params`, and `mod_color_calculate_degamma_params`.

Control flow: Callers set up X point distribution early, optionally precompute PQ tables, and call regamma/degamma calculators with transfer-function objects and optional user ramps. `calculate_buffer` is provided by the caller so expensive gamma intermediates can be reused during one curve build.

State and persistence: The header defines caller-visible state containers but no storage. `regamma_lut` overlays ramp and coefficient representations based on flags. HDR params carry luminance values and skip flag for FreeSync HDR tone mapping.

Dependencies and integration points: Includes `color_table.h` and forward-declares DC color types. Used by OPP/DPP color programming and FreeSync/HDR paths that need distributed transfer-function points.

Risks: Several bitfield comments use ADL/escape compatibility, so layout and flag meanings must stay stable. `calculate_buffer.buffer_index` has semantic sentinel use (`-1` after calculation in implementation) despite being int; callers must not reuse without initialization. HDR luminance units differ between min values and max values.

Test signals: Compile ABI checks for regamma flag bit layout, regamma ramp/coeff selection, HDR parameter unit tests, and API behavior for map-user-ramp and ROM-usage combinations.
