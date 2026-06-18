# sources/distributed-fs/ceph-client/include/media/tpg/v4l2-tpg.h

## Purpose
Defines the V4L2 test pattern generator state, supported patterns, color tables, configuration setters, geometry helpers, and buffer fill APIs.

## Important APIs, Types, and Functions
Types include RGB color structs, `enum tpg_color`, `tpg_pattern`, `tpg_quality`, video/pixel aspect enums, movement mode, color encoding, and the large `struct tpg_data`. External tables provide colors and transfer-function conversion data. APIs include `tpg_init()`, `tpg_alloc()`, `tpg_free()`, source reset, status logging, font/text generation, buffer fill, fourcc selection, crop/compose, color order, movement update, and many inline setters/getters for pattern, quality, color controls, colorspace, quantization, planes, line sizes, field, fill percentage, aspect, border/square, SAV/EAV, HDMI guard band, movement, and flips.

## Control Flow
Drivers initialize and allocate the TPG, configure format/color/geometry/pattern, then call fill helpers per plane/buffer. Setters mark `recalc_colors`, `recalc_lines`, or `recalc_square_border`, causing implementation code to rebuild cached lines/colors before generating frames. Movement counters update per frame/field.

## State and Persistence Behavior
`struct tpg_data` is persistent per generator instance and owns geometry, color configuration, format layout, recalc flags, allocated line buffers, random/contrast/black lines, and movement counters. State resets through explicit init/reset/free calls.

## Dependencies and Integration Points
Depends on V4L2 UAPI types, random/slab/vmalloc, and errno. Used by virtual/video test drivers to synthesize deterministic capture/output frames across many pixel formats.

## Risks
Plane/line-size math is format-sensitive; wrong downsampling or bytesperline handling can overrun buffers. Recalc flags must be set whenever dependent controls change. Movement and flip interaction affects static-pattern optimization.

## Test Signals
All pattern generation, RGB/YUV/HSV/luma formats, multiplanar/interleaved layouts, crop/compose scaling, h/v flip, moving square/border, text rendering, SAV/EAV and HDMI guard-band insertion, noise/static detection, and buffer-size boundary tests.
