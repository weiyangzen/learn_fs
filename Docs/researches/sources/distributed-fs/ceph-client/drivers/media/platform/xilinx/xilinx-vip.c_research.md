# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.c

Purpose: shared helper library for Xilinx Video IP drivers. It maps Xilinx AXI4 video formats to media-bus codes and V4L2 fourccs, provides register read/modify/write helpers through the header, initializes common MMIO/clock resources, and supplies generic subdev enum helpers.

Important APIs: exported functions are `xvip_get_format_by_code`, `xvip_get_format_by_fourcc`, `xvip_of_get_format`, `xvip_set_format_size`, `xvip_clr_or_set`, `xvip_clr_and_set`, `xvip_init_resources`, `xvip_cleanup_resources`, `xvip_enum_mbus_code`, and `xvip_enum_frame_size`. The static `xvip_video_formats[]` table covers YUV, RGB, monochrome, and Bayer formats with bpp/fourcc metadata.

Control flow: format lookup scans the static table; OF parsing reads `xlnx,video-format`, `xlnx,video-width`, and optional `xlnx,cfa-pattern`; resource initialization maps BAR/resource 0 and enables the device clock; enum helpers report the currently configured TRY format code and min/max frame sizes for simple sink/source subdevices.

State and persistence: no global mutable state. Per-device state is in `struct xvip_device`, especially `iomem`, `clk`, and `saved_ctrl` handled by header inline helpers.

Dependencies and integration: uses platform resource mapping, common clock framework, device-tree properties, dt-bindings `xilinx-vip.h`, V4L2 subdev states, and exported GPL symbols consumed by Xilinx TPG/VTC/DMA/composite code.

Risks: format table incompleteness silently defaults fourcc lookup to YUYV; OF format mismatch returns errors that stop probing; `xvip_init_resources()` enables clocks but ignores `clk_prepare_enable()` return. Test signals include DT format parsing, all exported symbol users building as modules, format lookup coverage, and subdev enum behavior for TRY versus ACTIVE formats.
