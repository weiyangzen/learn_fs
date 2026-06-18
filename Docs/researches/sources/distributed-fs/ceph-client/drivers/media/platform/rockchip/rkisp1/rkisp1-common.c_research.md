# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-common.c

Purpose: shared format and crop helpers for the RKISP1 driver.

Important APIs/types/functions: defines the `rkisp1_formats` media-bus table and exports `rkisp1_mbus_info_get_by_index()`, `rkisp1_mbus_info_get_by_code()`, `rkisp1_sd_adjust_crop_rect()`, `rkisp1_sd_adjust_crop()`, and `rkisp1_bls_swap_regs()`. The format table covers YUV source, Bayer sink/source RAW 8/10/12 with CSI-2 data type, bus width, and Bayer pattern, plus YUV sink formats with acquisition sequence bits.

Control flow: subdevs use index/code lookups for enumeration and validation; ISP/CSI/capture/resizer modules use returned metadata to choose acquisition mode, MIPI data type, Bayer pattern, output conversion, and media-bus compatibility. Crop helpers enforce RKISP1 minimum dimensions and map requested rectangles inside bounds.

State and persistence: static immutable format table only; helper functions mutate caller-provided crop/output arrays.

Dependencies/integration: depends on V4L2 media-bus constants, MIPI CSI-2 data types, V4L2 rect helpers, and register bit definitions from `rkisp1-regs.h`.

Risks: the format table is a single source of truth; omissions or wrong direction flags break enumeration and stream validation across multiple subdevs. `rkisp1_bls_swap_regs()` indexes a fixed pattern table and assumes a valid Bayer pattern enum from format metadata.

Test signals: format enumeration on CSI/ISP/resizer/capture, media pipelines using all Bayer patterns and YUV orders, crop boundary tests, and BLS register ordering tests when changing Bayer pattern.
