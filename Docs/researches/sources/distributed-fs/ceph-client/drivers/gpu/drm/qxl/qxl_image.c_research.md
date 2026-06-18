# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_image.c

Purpose: This file allocates and initializes QXL bitmap image objects used by draw commands.

Important APIs, types, and functions: `qxl_image_alloc_objects()` creates a `qxl_drm_image`, its descriptor BO, and one data chunk BO; `qxl_image_init()` copies framebuffer pixels into the chunk and fills `struct qxl_image`; `qxl_image_free_objects()` releases image/chunk BOs.

Control flow: Allocation creates a release-associated image BO and chunk BO sized for `height * stride` plus protocol headers. Initialization offsets source data by x/y, writes chunk metadata, copies contiguous or row-by-row pixel data across pages into the chunk, fills image descriptor fields, maps depth 1/24/32 to SPICE bitmap formats, marks images top-down, and stores the chunk physical address in the bitmap.

State and persistence: Image and chunk BOs are transient release-owned GPU-visible objects. Their contents persist until the host consumes and releases the draw command.

Dependencies and integration points: Used by `qxl_draw_dirty_fb()`. Depends on release-attached BO allocation, QXL BO atomic mapping helpers, SPICE image protocol definitions, and QXL physical address computation.

Risks: The code has explicit TODO/FIXME notes for integer overflow and variable chunk counts. It supports only 1, 24, and 32 bpp; 16 bpp dirty paths would fail. The chunk uses framebuffer stride rather than packed line size due to rendering concerns, which affects memory size and host interpretation.

Test signals: Dirty draw paths for 24/32 bpp, unsupported-depth rejection, very large dirty rectangles, non-contiguous row copying where `stride != linesize`, and allocation failure cleanup.
