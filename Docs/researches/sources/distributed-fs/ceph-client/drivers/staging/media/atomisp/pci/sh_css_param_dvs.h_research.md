# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_dvs.h

Purpose: `sh_css_param_dvs.h` defines the DVS table geometry and declares the DVS 6-axis table helpers. It is the shared sizing contract used by the DVS table allocator and the main ISP parameter writer.

Important APIs/types/functions: macros define minimum DVS envelope, block dimensions for luma/chroma, block count rounding, table dimensions, coordinate fraction bits, input bytes per pixel, xmem alignment, `DVS_6AXIS_COORDS_ELEMS`, `DVS_6AXIS_BYTES(binary)`, and the supported GDC interpolation mode. Declarations cover `generate_dvs_6axis_table()`, `generate_dvs_6axis_table_from_config()`, `free_dvs_6axis_table()`, and `copy_dvs_6axis_table()`.

Control flow and state: no runtime state exists. The macros determine allocation sizes and DDR buffer sizes at runtime when invoked with frame or binary dimensions. `DVS_NUM_BLOCKS_X()` rounds luma horizontal blocks to an even count, while chroma uses direct rounded-up block count.

Dependencies and integration: it includes Linux math helpers, `math_support.h`, CSS public types, and `gdc_global.h` for `gdc_warp_param_mem_t`. `sh_css_params.c` uses `DVS_6AXIS_BYTES(binary)` to size DVS parameter buffers and `sh_css_param_dvs.c` uses table dimension macros to allocate coordinate arrays.

Risks: `DVS_6AXIS_BYTES(binary)` currently references only `out_frame_info[0]` and assumes two outputs have the same resolution, as the comment states. Format assumptions are YUV420-like for UV dimensions. Size macros can overflow if binary resolution is invalid or unbounded.

Test signals: geometry tests should verify luma/chroma block and table sizes for even/odd widths, minimum envelope handling, and DDR byte counts for binaries with DVS enabled. Integration tests should compare generated buffer sizes against firmware consumption.
