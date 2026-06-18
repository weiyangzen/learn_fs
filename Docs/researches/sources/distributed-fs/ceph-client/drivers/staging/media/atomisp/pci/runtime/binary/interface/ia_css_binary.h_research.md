# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/interface/ia_css_binary.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/interface/ia_css_binary.h` declares the central CSS binary-selection and binary-metadata API, including mode constants, descriptor structs, selected-binary state, grid/shading helpers, parameter lifetime helpers, and ISP binary enumeration.

Important APIs, types, and functions: Important local symbols: `ia_css_binary_init_infos`, `ia_css_binary_uninit`, `ia_css_binary_fill_info`, `ia_css_binary_find`, `ia_css_binary_get_shading_info`, `ia_css_binary_3a_grid_info`, `ia_css_binary_dvs_grid_info`, `ia_css_binary_dvs_stat_grid_info`, `ia_css_binary_max_vf_width`, `ia_css_binary_destroy_isp_parameters`, `ia_css_binary_get_isp_binaries` Types and constants: `ia_css_cas_binary_descr`, `ia_css_binary_descr`, `ia_css_binary`; `_IA_CSS_BINARY_H_`, `IA_CSS_BINARY_MODE_COPY`, `IA_CSS_BINARY_MODE_PREVIEW`, `IA_CSS_BINARY_MODE_PRIMARY`, `IA_CSS_BINARY_MODE_VIDEO`, `IA_CSS_BINARY_MODE_PRE_ISP`, `IA_CSS_BINARY_MODE_GDC`, `IA_CSS_BINARY_MODE_POST_ISP`, `IA_CSS_BINARY_MODE_ANR`, `IA_CSS_BINARY_MODE_CAPTURE_PP`

Control flow: Pipeline code fills `ia_css_binary_descr`, calls `ia_css_binary_find()`, receives a populated `ia_css_binary`, then queries grid/shading/VF limits and eventually destroys allocated ISP parameters.

State and persistence behavior: State is process-local firmware metadata (`all_binaries`, `binary_infos`), loaded blob XMEM addresses, per-selected-binary frame/grid/table metrics, and allocated ISP parameter segments. `ia_css_binary_uninit()` and `ia_css_binary_destroy_isp_parameters()` release that state; nothing is file-backed.

Dependencies and integration points: Binary selection depends on `sh_css_blob_info`, HMM allocation, ISP parameter allocation, frame/public CSS types, VF/SC/SDIS helpers, firmware metadata, DVS/BDS macros, and AtomISP logging.

Risks and edge cases: The descriptor combines many boolean feature gates and frame-info pointers; invalid combinations are mostly rejected in implementation rather than by the type system.

Test signals: Cover each binary mode, online/offline input sources, VF and no-VF outputs, multiple output pins, BDS factors, high-speed/reduced/continuous/striped variants, DVS envelope sizing, unsupported formats, firmware-load failure, and parameter cleanup after partial fill failure.
