# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lut.c

Purpose: implements the VSP1 1D look-up table processor. It exposes a 256-entry U32 V4L2 control, enables the LUT hardware, and injects table writes into display lists.

Important APIs and functions: `vsp1_lut_create()`, `lut_set_table()`, `lut_s_ctrl()`, `lut_configure_stream()`, `lut_configure_frame()`, and `lut_destroy()`. Supported media bus codes are ARGB, AHSV, and AYUV 32-bit formats.

Control flow: table control updates allocate a display-list body, write all `VI6_LUT_TABLE + 4*i` entries, swap the pending body under a spinlock, and drop the local reference. Stream configuration writes `VI6_LUT_CTRL_EN`. Per-frame configuration consumes any pending table body by adding it to the current display list and releasing the local reference.

State and persistence: `struct vsp1_lut` stores control handler, spinlock, pending table body, and body pool. LUT table updates persist as DMA-backed display-list entries rather than direct register writes. The pool has three bodies to tolerate queued/pending hardware updates.

Dependencies and integration: depends on V4L2 custom controls, common entity pad helpers, display-list body pools, and route setup. Created only on feature-enabled variants.

Risks and test signals: risks include pool exhaustion on rapid updates, update coalescing through swap semantics, and table payload validation. Test control updates while streaming, graph insertion/removal, visual LUT effect, and cleanup under active queued lists.
