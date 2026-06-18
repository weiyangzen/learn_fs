<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fu.c

Purpose: Provides common fetchunit register programming for i.MX8 DC FetchLayer and FetchWarp blocks.

Important APIs/types/functions: Exports `dc_fu_get_pixel_format_bits()`, `dc_fu_get_pixel_format_shifts()`, `dc_fu_shdldreq_sticky()`, `dc_fu_set_src_bpp()`, `dc_fu_common_hw_init()`, `dc_fu_get_ops()`, and the `dc_fu_common_ops` table.

Control flow: Common ops set burst length from base-address alignment, base address, stride, source dimensions, source buffer enable/disable, and layerblend association. Hardware init disables base-address autoupdate, enables shadowing, sets display line mode, configures 16 buffers, initializes layer/clip windows, disables all source buffers, and clears blend mode/constant color.

State and persistence behavior: Mutates fetchunit hardware registers through the `dc_fu` regmap. Also stores the currently associated layerblend in `fu->lb` so disabling the source can disable the blend clock and put the layerblend in neutral mode.

Dependencies: Regmap, bitfield helpers, Linux math helpers, DRM fourcc, and layerblend helpers from `dc-pe.h`.

Integration points: FetchLayer and FetchWarp install these ops and override only format/framedimension/init specifics. Plane update calls these ops through `dc_fu_get_ops()`.

Risks: Pixel-format lookup leaves output unchanged if the format is unknown; callers rely on prior atomic format restrictions. Burst-length calculation from `__ffs(baddr)` assumes non-zero base addresses and alignment already checked.

Test signals: Plane update register programming, base-address alignment cases, source disable clearing layerblend, runtime resume common init, and format table coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fu.c -->
