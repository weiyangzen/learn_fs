# sources/compression/zstd/tests/cli-tests/compression/stream-size.sh

## Purpose
This test validates CLI support for content-size metadata and compression size hints on streaming stdin input.

## APIs, control flow, and integration
It pipes `datagen -g7654` into `zstd --stream-size=7654` and into `zstd --size-hint=7000`, then pipes both compressed streams to `zstd -t`. The script does not create named files.

## State, dependencies, risks, and test signals
There is no persistent state beyond pipeline buffers. Dependencies are `datagen` and CLI option support. Risks are limited because it validates decompression, not metadata inspection; it catches malformed frames and parser failures but not necessarily incorrect optional size fields.
