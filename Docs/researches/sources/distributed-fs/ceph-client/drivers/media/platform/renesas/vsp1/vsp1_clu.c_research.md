# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_clu.c

Purpose: implements the VSP1 cubic look-up table processor. It exposes a V4L2 subdevice with 2D/3D mode control and a 17x17x17 U32 LUT control, then injects LUT table programming into display lists.

Important APIs and functions: `vsp1_clu_create()`, `clu_set_table()`, `clu_s_ctrl()`, `clu_configure_stream()`, `clu_configure_frame()`, and `clu_destroy()`. Supported media bus formats are ARGB, AHSV, and AYUV 32-bit packed formats.

Control flow: userspace writes LUT and mode controls. Table updates allocate a display-list body from a small pool, write `VI6_CLU_ADDR` and all `VI6_CLU_DATA` entries, then swap it into `clu->clu` under a spinlock. Stream configuration caches whether the stream is AYUV. Per-frame configuration enables CLU, optionally sets 2D mode when requested and YUV, then consumes the pending LUT body by adding it to the current display list and dropping the local reference.

State and persistence: persistent control state includes `mode`, `yuv_mode`, pending `clu` display-list body, and the body pool. The table is not written directly to MMIO; it persists as queued DMA display-list entries until consumed by hardware. Spinlock protects table-body handoff between control updates and frame configuration.

Dependencies and integration: depends on V4L2 custom controls, common entity pad helpers, `vsp1_dl_body_pool_create()`, and display-list body ownership rules.

Risks and test signals: risks include pool exhaustion on rapid table updates, lost updates due to swap semantics, 2D mode only being valid for YUV, and large control payload validation. Test by setting CLU table while streaming, checking memory leak/refcount behavior, toggling 2D/3D modes, and validating visual output or register traces.
