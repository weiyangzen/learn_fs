# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_regs.h

Purpose: register offset and bitfield macro catalog for the Allwinner Cedrus video engine used by MPEG, H264, H265, VP8, and some ISP/AVC-related blocks.

Important APIs/macros: `SHIFT_AND_MASK_BITS()` is the common field packer. Common engine offsets define `VE_MODE`, buffer control, primary/secondary output formats, strides, and version. MPEG macros cover picture headers, coded/bound sizes, control/trigger/status, bitstream addresses, reconstruction/reference addresses, quant matrix input, and error/MB status. H265 macros cover NAL/SPS/PPS/slice headers, CTB addresses, control/trigger/status, bitstream addresses, tile/entry-point/scaling-list/SRAM registers, frame info offsets, ref lists, and 10-bit configuration. H264/VP8 macros share the H264 engine space for SPS/PPS/slice, VLD, SRAM port, trigger/status, VP8 probability/segmentation/filter/refs, and output addresses.

Control flow: no executable flow; codec and hardware source files compose register values through these macros before `cedrus_write()`.

State and persistence: defines hardware ABI constants only.

Dependencies/integration: included by all Cedrus codec/hardware implementations. It assumes Linux `BIT()`, `GENMASK()`, `DIV_ROUND_UP()`, and alignment helpers are available through included kernel headers.

Risks: field macros often mask shifted values but do not validate input range; callers must bound values from V4L2 controls. Address base macros drop low bits or reorder high bits according to hardware requirements; wrong buffer alignment or DMA address width assumptions can corrupt decode. The file also contains unused/less-used ISP/AVC offsets that may not be exercised by current decode paths.

Test signals: compile-time macro use across all codecs, register trace comparison against known-good BSP values, high DMA address tests for address packing, tiled/untiled output validation, and 10-bit HEVC output layout tests.
