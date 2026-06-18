# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/src/binary.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/src/binary.c` implements CSS ISP binary inventory, matching, sizing, grid/shading metadata, parameter allocation, and cleanup.

Important APIs, types, and functions: Important local symbols: `ia_css_binary_dvs_env`, `ia_css_binary_internal_res`, `ia_css_binary_compute_shading_table_bayer_origin`, `binary_get_shading_info_type_1`, `ia_css_binary_get_shading_info`, `sh_css_binary_common_grid_info`, `ia_css_binary_dvs_grid_info`, `ia_css_binary_dvs_stat_grid_info`, `ia_css_binary_3a_grid_info`, `binary_init_pc_histogram`, `binary_init_metrics`, `binary_supports_output_format`, `binary_supports_vf_format`, `supports_bds_factor` Types and constants: `sh_css_shading_table_bayer_origin_compute_results`; `MAX_SPEC_DECI_FACT_LOG2`, `MIN_SPEC_DECI_FACT_LOG2`, `DECI_FACT_LOG2_5_SMALLEST_FRAME_WIDTH_BQ`, `DECI_FACT_LOG2_4_SMALLEST_FRAME_WIDTH_BQ`

Control flow: `ia_css_binary_init_infos()` loads ISP firmware blobs into `all_binaries` and mode lists. `ia_css_binary_find()` filters candidates by continuity, striping, pipe version, feature flags, input source, output/VF formats, frame sizes, BDS/DPC, and then calls `ia_css_binary_fill_info()`. Fill-info allocates ISP parameters, derives internal/input/output/VF sizes, DVS envelope, morph and statistics table dimensions, DIS info, and left padding.

State and persistence behavior: State is process-local firmware metadata (`all_binaries`, `binary_infos`), loaded blob XMEM addresses, per-selected-binary frame/grid/table metrics, and allocated ISP parameter segments. `ia_css_binary_uninit()` and `ia_css_binary_destroy_isp_parameters()` release that state; nothing is file-backed.

Dependencies and integration points: Binary selection depends on `sh_css_blob_info`, HMM allocation, ISP parameter allocation, frame/public CSS types, VF/SC/SDIS helpers, firmware metadata, DVS/BDS macros, and AtomISP logging.

Risks and edge cases: Candidate matching is order-sensitive, has many early `continue` gates, and mixes firmware metadata with caller frame descriptors; small mistakes can select no binary or a subtly wrong binary.

Test signals: Cover each binary mode, online/offline input sources, VF and no-VF outputs, multiple output pins, BDS factors, high-speed/reduced/continuous/striped variants, DVS envelope sizing, unsupported formats, firmware-load failure, and parameter cleanup after partial fill failure.
