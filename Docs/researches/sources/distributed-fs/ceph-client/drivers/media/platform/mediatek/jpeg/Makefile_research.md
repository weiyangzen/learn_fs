# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/Makefile

## Purpose
This Makefile builds the MediaTek JPEG mem2mem driver and its encode/decode hardware helper objects when `CONFIG_VIDEO_MEDIATEK_JPEG` is enabled.

## Important APIs, Types, And Functions
The build rules add `mtk_jpeg.o`, `mtk-jpeg-enc-hw.o`, and `mtk-jpeg-dec-hw.o` under `CONFIG_VIDEO_MEDIATEK_JPEG`. `mtk_jpeg-y` is composed from `mtk_jpeg_core.o` and `mtk_jpeg_dec_parse.o`. The encode and decode hardware modules are built from `mtk_jpeg_enc_hw.o` and `mtk_jpeg_dec_hw.o`.

## Control Flow And State
Build state follows the Kconfig tristate. The split object layout keeps the V4L2/mem2mem core and JPEG header parser in one logical module object, with hardware-specific encode/decode helpers as additional objects.

## Dependencies And Integration Points
This file maps to `mtk_jpeg_core.c`, `mtk_jpeg_core.h`, parser code, and encode/decode hardware accessors. The core includes both encode and decode hardware headers and chooses behavior through OF match variant data.

## Risks
The object names use both underscores and hyphens. Module/object renames must update all composite assignments consistently. If hardware helper symbols are referenced by the core, omitting either helper from the config build will fail link.

## Test Signals
Build `CONFIG_VIDEO_MEDIATEK_JPEG=m` and verify that the resulting module contains core, parser, encoder hardware, and decoder hardware code. Build all OF variant paths to catch missing helper symbols.
