# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga.h

Purpose: declares the internal data structures and helpers shared by the Rockchip RGA V4L2 driver, buffer code, and hardware command code.

Important APIs/types: `struct rga_fmt` maps V4L2 fourcc to depth, subsampling factors, color swap, and hardware format. `struct rga_frame` stores dimensions, colorspace, crop, format, V4L2 pix format, stride, and total size. `struct rga_ctx` is per-file state with m2m file handle, input/output frames, controls, sequences, transform controls, and fill color. `struct rockchip_rga` is device-wide state with V4L2/m2m/video devices, MMIO, clocks, version, mutex, control spinlock, current context, and command buffer. `struct rga_vb_buffer` extends VB2 buffers with RGA MMU descriptors and plane offsets.

Control flow/state: `file_to_rga_ctx()` and `vb_to_rga()` provide container conversion. Inline `rga_write()`, `rga_read()`, and `rga_mod()` encapsulate MMIO. `rga_get_frame()`, `rga_qops`, and `rga_hw_start()` are cross-file entry points.

Dependencies/integration: included by `rga.c`, `rga-buf.c`, and `rga-hw.c`; depends on V4L2 controls/device and videobuf2-v4l2 types.

Risks and test signals: shared structure layout affects buffer allocation and hardware programming. The unused `regmap *grf` and `op` fields may be legacy or future hooks. Test builds with sparse/compiler warnings and runtime operations that touch each shared field: format setup, controls, queueing, command start, IRQ completion, and cleanup.
