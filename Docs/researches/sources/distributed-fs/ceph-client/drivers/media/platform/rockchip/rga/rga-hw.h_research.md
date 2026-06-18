# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-hw.h

Purpose: declares Rockchip RGA hardware limits, register offsets, field values, format IDs, and bitfield unions used to build command buffers.

Important definitions: size limits include min/default/max width and height plus `RGA_TIMEOUT`. Register macros cover system, command, interrupt, MMU, version, source/destination base addresses, virtual/active sizes, scaling factors, colors, alpha/fading/pattern/ROP, and MMU descriptor bases. Format macros define RGB/YUV/palette IDs and helpers `RGA_COLOR_FMT_IS_YUV()`/`RGA_COLOR_FMT_IS_RGB()`. Unions model `RGA_MODE_CTRL`, source/destination info, virtual/active info, scale factors, transparency, alpha controls, fading, and pattern registers.

Control flow/state: no runtime state; unions are local packing helpers used by `rga-hw.c` to write 32-bit command-buffer words.

Dependencies/integration: included by all RGA source files. Values must match hardware and the driver format table in `rga.c`.

Risks and test signals: C bitfield layout can be compiler/endianness sensitive in general, though this driver relies on target layout. Bad register values affect every transform. Test by comparing command buffer dumps to known-good hardware programming and compiling across supported architectures for warnings.
