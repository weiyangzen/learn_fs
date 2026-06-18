# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_parse.c

## Purpose
This file parses enough of a JPEG bitstream to extract baseline SOF0 image properties needed by the MediaTek JPEG decoder hardware. It reads dimensions, component count, component IDs, sampling factors, and quantization table selectors, then asks the hardware helper to derive decoder configuration.

## Important APIs, Types, and Functions
`struct mtk_jpeg_stream` is a small bounds-checked cursor over the mapped source buffer. `read_byte()`, `read_word_be()`, and `read_skip()` implement marker walking. `mtk_jpeg_do_parse()` scans markers and fills `struct mtk_jpeg_dec_param`. `mtk_jpeg_parse()` is the exported parser entry that also calls `mtk_jpeg_dec_fill_param()`.

## Control Flow
The parser scans until it sees marker prefix `0xff`, skips fill bytes, ignores stuffed zero bytes, and switches on the marker code. SOI, EOI, TEM, and restart markers have no length payload. Unknown/unused markers are skipped using their big-endian length. On SOF0 it reads precision, height, width, component count, and per-component ID/sampling/quant table fields; success requires one or three complete components. It returns false if the stream ends or derived hardware parameters are unsupported.

## State and Persistence
All parser state is stack-local except for fields written into the caller-provided `struct mtk_jpeg_dec_param`. There is no persistence beyond the decode job.

## Dependencies and Integration Points
The parser depends on Linux media JPEG marker constants from `<media/jpeg.h>`, V4L2 types, and `mtk_jpeg_dec_fill_param()` from the hardware helper. It integrates with the JPEG core before queueing/configuring a decode job.

## Risks and Edge Cases
Only SOF0 baseline frames are accepted; progressive or other SOF markers are not parsed. `read_skip()` repeatedly consumes bytes and ignores short-skip failure, so a truncated non-SOF segment only fails on a later read. Component arrays rely on `comp_num` being one or three. The code uses `int` for byte reads and stores into unsigned fields, making `-1` checks critical before assignment.

## Test Signals
Feed valid baseline grayscale and YUV JPEG headers, progressive JPEGs, truncated headers, marker stuffing/fill-byte sequences, restart markers before SOF0, invalid component counts, and unsupported sampling factors. Expected signals are boolean parse results and correctly derived decoder formats/strides.
