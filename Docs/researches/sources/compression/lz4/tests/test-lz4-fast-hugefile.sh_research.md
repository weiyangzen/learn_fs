# sources/compression/lz4/tests/test-lz4-fast-hugefile.sh

## Purpose
This shell test is huge-file coverage for fast LZ4 paths and sparse decompression. It exercises data sizes beyond 32-bit boundaries and verifies two sparse outputs generated through different content-size settings are equivalent.

## Important Control Flow
The script streams 6 GiB through `lz4 -vB5` and test mode, then creates two 3 GiB sparse decompressed files using `--sparse`, one without and one with `--content-size`. It compares the two outputs with `diff -s` and prints block allocation via `ls -ls`.

## State, Dependencies, and Integration
Temporary files use `tmp-lfh` and are removed on EXIT. It depends on `datagen`, `lz4`, `diff`, and enough filesystem support for sparse files. It targets the CLI and frame size handling, especially paths that process inputs larger than 2 GiB.

## Risks and Test Signals
The test is resource-heavy and can be unsuitable for small CI machines. It gives strong regression signals for integer overflow, content-size handling on large streams, and sparse output creation, but does not compare against a full non-sparse reference to avoid disk cost.
