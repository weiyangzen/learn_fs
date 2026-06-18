# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_dvs.c

Purpose: `sh_css_param_dvs.c` allocates, initializes, copies, and frees DVS 6-axis coordinate tables and translates ISP DVS statistics into host structures. These tables drive digital video stabilization coordinate warping for luma and chroma planes.

Important APIs/types/functions: internal `alloc_dvs_6axis_table()` allocates the config wrapper and four coordinate arrays. `init_dvs_6axis_table_from_default()` fills unity/default coordinates from frame resolution and DVS offset. `init_dvs_6axis_table_from_config()` copies an existing table. Exports are `generate_dvs_6axis_table()`, `generate_dvs_6axis_table_from_config()`, `free_dvs_6axis_table()`, `copy_dvs_6axis_table()`, and `ia_css_dvs_statistics_get()`.

Control flow and state: allocation chooses dimensions from either a source config or frame resolution using macros from `sh_css_param_dvs.h`; it then allocates Y x/y and UV x/y arrays and unwinds on failure. Default initialization walks each grid and stores coordinates shifted by `DVS_COORD_FRAC_BITS`, with UV offsets half of Y offsets and chroma block height. Copy helpers assert matching dimensions and memcpy the four arrays. Statistics dispatch selects DVS1 or DVS2 conversion based on `enum dvs_statistics_type`.

Dependencies and integration: it depends on DVS table geometry macros, CSS debug/assert/type headers, and statistics conversion helpers such as `ia_css_get_dvs_statistics()` and `ia_css_get_dvs2_statistics()`. `sh_css_params.c` uses these tables when generating per-pipe DVS 6-axis parameter buffers and user-visible DVS2 6-axis configs.

Risks: assertions enforce dimension invariants but may be compiled out, after which mismatched tables can overflow during `memcpy()`. Coordinate size arithmetic uses unsigned products and should be validated for overflow on large resolutions. Comments contain legacy YUV420 assumptions; other formats may not match UV sizing. `ia_css_dvs_statistics_get()` silently does nothing for unknown types.

Test signals: tests should allocate and free tables for small, odd, and maximum resolutions, verify default coordinate formulas, copy between same-sized tables, inject allocation failures at each array, and translate both DVS and DVS2 statistics. Sanitizer tests should check dimension mismatch behavior.
