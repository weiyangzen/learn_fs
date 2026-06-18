# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_osd_afbcd.c

Purpose: Implements AFBC decoder operation tables for Meson OSD primary-plane compressed framebuffers. It supports the Amlogic GXM AFBC 1.0 decoder and the ARM Mali AFBC decoder on G12A, translating DRM modifiers/formats and staged plane state into decoder register programming.

Important APIs, types, and functions: Exports `meson_afbcd_gxm_ops` and `meson_afbcd_g12a_ops` as `struct meson_afbcd_ops`. GXM helpers include pixel-format validation, reset, enable/disable, and setup for OSD1_AFBCD registers. G12A helpers include pixel-format, bits-per-pixel, block-mode mapping, RDMA-backed reset/init/enable/setup, and format support checks.

Control flow: Plane update sets `priv->afbcd.modifier`, `format`, OSD size/address, and then the broader VIU commit path can call these ops. GXM setup writes mode flags, input size, header/frame/chroma pointers, line-buffer length, and pixel scopes directly. G12A init allocates/sets up RDMA and asserts manual reset. G12A setup queues format specifier, buffer dimensions, bounding box, output internal address, and output stride through `meson_rdma_writel_sync()`. G12A enable masks AFBC IRQs, enables surface 0, issues direct swap, and flushes RDMA so writes replay on VSYNC.

State and persistence: Uses `priv->afbcd` for modifier/format and `priv->viu` for width, height, and framebuffer DMA address. G12A owns `priv->rdma` coherent descriptor state while active. Hardware state persists in AFBCD/MAFBC registers and, on G12A, in the RDMA channel trigger list.

Dependencies and integration points: Depends on DRM fourcc AFBC modifier definitions, `meson_plane.c` modifier checks, `meson_rdma`, and register constants from `meson_registers.h`. G12A decoded output goes to fixed internal address `MESON_G12A_AFBCD_OUT_ADDR` from the header and is consumed by OSD unpacking.

Risks: GXM supports only XBGR/ABGR RGB32 with YTR and no 32x8 blocks. G12A rejects YTR on non-XBGR formats and leaves YUV support as TODO. Several magic register values are undocumented. G12A RDMA buffer overflow is only warned once by RDMA helper. Fixed internal output address must match hardware expectations and not normal memory.

Test signals: AFBC primary-plane scanout on GXM and G12A, modifier rejection for unsupported YTR/block combinations, visual validation of RGB565/RGB888/XRGB/ARGB/XBGR/ABGR on G12A, VSYNC-synchronized AFBC updates, and decoder reset/disable on plane disable.
