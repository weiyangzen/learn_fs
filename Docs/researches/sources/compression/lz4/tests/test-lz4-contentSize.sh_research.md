# sources/compression/lz4/tests/test-lz4-contentSize.sh

## Purpose
This shell test verifies when LZ4 frame content-size metadata is emitted and preserved. It distinguishes regular file input, redirection from a seekable file, and piped stdin where the size cannot be known.

## Important Control Flow
The script creates a 15 MiB deterministic file, compresses it with and without `--content-size`, decompresses to prove round-trip correctness, and compares compressed outputs to assert whether content-size metadata changed the frame. It uses `diff ... && exit 1` where two outputs must differ.

## State, Dependencies, and Integration
Temporary files use the `tmp-lzc` prefix and are removed on EXIT. Dependencies are `datagen`, `lz4`, `diff`, `cat`, and shell redirection semantics. This integrates with frame-header behavior in the `lz4` CLI and frame decoder.

## Risks and Test Signals
The key signal is that `--content-size` only works when the input size is discoverable. The test also confirms compatibility of frames with content size by decoding and comparing against the original. It does not inspect frame headers directly, so failures report via output equality rather than an explicit metadata parser.
