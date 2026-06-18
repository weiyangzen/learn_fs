# sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.c

## Purpose
`gzip_zinfo.c` implements gzip random-access checkpoint generation, extraction, and binary serialization. It is based on zlib `zran.c` but modified for SOCI zTOC span metadata, little-endian storage, gzip header handling, and concatenated gzip streams such as pigz output.

## Important APIs, Types, and Functions
Metadata functions include `pt_index_from_ucmp_offset`, `get_ucomp_off`, `get_comp_off`, `get_blob_size`, `get_max_span_id`, and `has_bits`. Generation functions include `generate_zinfo_from_fp` and `generate_zinfo_from_file`. Extraction functions include `extract_data_from_fp`, `extract_data_from_file`, and `extract_data_from_buffer`. Serialization functions include `zinfo_to_blob` and `blob_to_zinfo`. Internal helpers encode/decode little-endian integers, initialize zlib streams, add checkpoints, and free zinfo memory.

## Control Flow, State, and Persistence
Checkpoint generation inflates the gzip/zlib stream with `inflate(..., Z_BLOCK)`, records access points at block boundaries when uncompressed output has advanced beyond the requested span, captures the 32 KiB sliding dictionary, and stores compressed and uncompressed offsets. It supports concatenated gzip members by resetting inflate state after `Z_STREAM_END` when more input remains. Extraction seeks or slices to the checkpoint, primes partial bits if needed, installs the saved dictionary, skips to the requested uncompressed offset, and inflates into the destination. Blob persistence stores checkpoint count and span size header followed by packed checkpoint records; version 1 compatibility omits the first checkpoint while version 2 includes it.

## Dependencies and Integration Points
The implementation depends on zlib, C stdio/stdlib/string, endian conversion functions, and the public declarations in `gzip_zinfo.h`. Go cgo wrappers in `gzip_zinfo.go` call these functions for zTOC construction and extraction.

## Risks and Test Signals
Memory ownership is manual; Go calls `C.free` on the top-level pointer but this C file also provides `free_zinfo` because the checkpoint list is separately allocated. Incorrect freeing can leak `index->list`. `blob_to_zinfo` returns NULL for mismatched claimed sizes but leaks the allocated `index` on one invalid-size branch. Buffer extraction must avoid reading past the supplied compressed span; it tracks `remaining`, but malformed inputs can return zlib errors. Tests cover malformed blobs, empty data, zero-size reads, gzip header options, pigz concatenated streams, serialization round trips, and extraction across span sizes.
