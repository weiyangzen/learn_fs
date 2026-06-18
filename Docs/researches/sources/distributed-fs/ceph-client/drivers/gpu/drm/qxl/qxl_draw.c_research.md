# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_draw.c

Purpose: This file converts framebuffer dirty regions into QXL draw commands using bitmap image objects and clip rectangles.

Important APIs, types, and functions: `qxl_draw_dirty_fb()` is the exported drawing entry point. Internal helpers allocate clip BOs, set up `struct qxl_clip_rects`, allocate draw releases, and initialize `struct qxl_drawable` with copy operation metadata.

Control flow: For a dirtyfb call, the function allocates a drawable release, computes the bounding box of clip rectangles, allocates clip and image BOs attached to the release, reserves all release BOs, creates a `QXL_DRAW_COPY` drawable, maps the source framebuffer BO, initializes a QXL bitmap image from the dirty area, fills clip rectangles, fences the release BO list, and pushes the drawable to the command ring. Error paths back off reservations and free allocated image/clip/release objects.

State and persistence: The function creates transient release, image, and clip BOs that remain live until the host returns their release IDs. It reads framebuffer BO contents and writes host-visible QXL command payloads.

Dependencies and integration points: Called from `qxl_display.c` atomic primary updates and framebuffer `.dirty`. Depends on `qxl_image_alloc_objects()`, `qxl_image_init()`, release helpers, BO mapping helpers, and QXL command ring push.

Risks: Clip rectangles are aggregated into a single bounding image, so large sparse dirty regions can copy more data than necessary. The first clip rectangle is modified by `dumb_shadow_offset`, which mutates caller-provided clip storage. Error cleanup must avoid freeing releases after successful push. TODOs note missing optimized fill handling and known clip-list performance concerns.

Test signals: Dirtyfb with zero clips, multiple clips, annotated copy clips, dumb-shadow offsets, 24/32-bit formats, sparse dirty regions, and forced allocation/reservation failures.
