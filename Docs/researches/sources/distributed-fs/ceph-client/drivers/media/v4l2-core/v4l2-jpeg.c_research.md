# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-jpeg.c

## Purpose
`v4l2-jpeg.c` provides V4L2 JPEG helper data and a bounded JPEG header parser for kernel JPEG codec drivers. It exports standard Annex K quantization and Huffman reference tables, the zigzag scan order, and `v4l2_jpeg_parse_header()` for parsing marker segments up to the start of entropy-coded data.

## Important APIs, Types, And Functions
The public exports are the reference table arrays, `v4l2_jpeg_zigzag_scan_index`, and `v4l2_jpeg_parse_header(void *buf, size_t len, struct v4l2_jpeg_header *out)`. Internally, `struct jpeg_stream` tracks the current and end byte pointers. `jpeg_get_byte()`, `jpeg_get_word_be()`, and `jpeg_skip()` enforce buffer bounds. Segment parsers fill `struct v4l2_jpeg_frame_header`, `struct v4l2_jpeg_scan_header`, `struct v4l2_jpeg_reference`, restart interval, and APP14 transform metadata.

## Control Flow
`v4l2_jpeg_parse_header()` verifies an initial SOI marker, initializes DHT/DQT counters and APP14 state, then loops through markers with `jpeg_next_marker()`. Baseline and extended sequential SOF markers are accepted; progressive, lossless, arithmetic, and unsupported SOF/DAC/TEM markers return `-EINVAL`. DHT and DQT segments are either referenced and skipped or parsed into caller-provided table arrays. DRI updates the restart interval. APP14 parses Adobe transform data if present. SOS records the scan header, sets `ecs_offset`, and returns, deliberately stopping before entropy-coded data.

## State And Persistence
The parser is stateless outside the caller-owned output structure. Segment references point directly into the supplied buffer, so callers must keep that buffer alive while using returned `start` pointers. The file has no persistent storage, no global mutable state, and no hardware interaction.

## Dependencies And Integration Points
The file depends on `<media/v4l2-jpeg.h>` for output structures and constants, Linux unaligned big-endian helpers, and kernel errno conventions. It integrates with JPEG mem2mem/stateless codec drivers that need to validate JPEG streams and program hardware with frame size, subsampling, quantization, Huffman, and restart data.

## Risks And Test Signals
Important risks are malformed length handling, table count wrapping into the four-reference arrays, reliance on SOF precision before DQT parsing, and rejecting valid JPEG variants outside the supported baseline/extended-sequential subset. Good tests include truncated buffers at every marker boundary, invalid SOF/DQT/DHT lengths, grayscale and 4-component subsampling cases, APP14 Adobe transform extraction, DRI parsing, DHT/DQT skip mode with NULL table arrays, and ensuring `ecs_offset` points just after SOS header parsing.
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-jpeg.c

## Purpose
`v4l2-jpeg.c` provides V4L2 JPEG helper data and a bounded JPEG header parser for kernel JPEG codec drivers. It exports standard Annex K quantization and Huffman reference tables, the zigzag scan order, and `v4l2_jpeg_parse_header()` for parsing marker segments up to the start of entropy-coded data.

## Important APIs, Types, And Functions
The public exports are the reference table arrays, `v4l2_jpeg_zigzag_scan_index`, and `v4l2_jpeg_parse_header(void *buf, size_t len, struct v4l2_jpeg_header *out)`. Internally, `struct jpeg_stream` tracks the current and end byte pointers. `jpeg_get_byte()`, `jpeg_get_word_be()`, and `jpeg_skip()` enforce buffer bounds. Segment parsers fill `struct v4l2_jpeg_frame_header`, `struct v4l2_jpeg_scan_header`, `struct v4l2_jpeg_reference`, restart interval, and APP14 transform metadata.

## Control Flow
`v4l2_jpeg_parse_header()` verifies an initial SOI marker, initializes DHT/DQT counters and APP14 state, then loops through markers with `jpeg_next_marker()`. Baseline and extended sequential SOF markers are accepted; progressive, lossless, arithmetic, and unsupported SOF/DAC/TEM markers return `-EINVAL`. DHT and DQT segments are either referenced and skipped or parsed into caller-provided table arrays. DRI updates the restart interval. APP14 parses Adobe transform data if present. SOS records the scan header, sets `ecs_offset`, and returns, deliberately stopping before entropy-coded data.

## State And Persistence
The parser is stateless outside the caller-owned output structure. Segment references point directly into the supplied buffer, so callers must keep that buffer alive while using returned `start` pointers. The file has no persistent storage, no global mutable state, and no hardware interaction.

## Dependencies And Integration Points
The file depends on `<media/v4l2-jpeg.h>` for output structures and constants, Linux unaligned big-endian helpers, and kernel errno conventions. It integrates with JPEG mem2mem/stateless codec drivers that need to validate JPEG streams and program hardware with frame size, subsampling, quantization, Huffman, and restart data.

## Risks And Test Signals
Important risks are malformed length handling, table count wrapping into the four-reference arrays, reliance on SOF precision before DQT parsing, and rejecting valid JPEG variants outside the supported baseline/extended-sequential subset. Good tests include truncated buffers at every marker boundary, invalid SOF/DQT/DHT lengths, grayscale and 4-component subsampling cases, APP14 Adobe transform extraction, DRI parsing, DHT/DQT skip mode with NULL table arrays, and ensuring `ecs_offset` points just after SOS header parsing.
