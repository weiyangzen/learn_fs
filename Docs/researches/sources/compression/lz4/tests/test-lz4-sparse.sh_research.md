# sources/compression/lz4/tests/test-lz4-sparse.sh

## Purpose
This shell test validates sparse decompression behavior, `--no-sparse`, console compatibility, and append-to-existing-output use cases.

## Important Control Flow
It generates all-zero-style data with `datagen -P100`, compresses with block sizes `B4D` through `B7D`, decompresses with `--sparse`, and compares each output. It checks an odd-sized sparse payload, then verifies stdin/stdout console paths and appending a decompressed stream with `>>` to create a doubled file reference.

## State, Dependencies, and Integration
Temporary files use `tmp-tls*`. Dependencies are `datagen`, `lz4`, `diff`, `ls`, `cat`, `printf`, and shell redirection. The test integrates with CLI file I/O, sparse write optimization, and frame options.

## Risks and Test Signals
The test is valuable for filesystem allocation and last-block edge cases, but sparse allocation effectiveness is only printed with `ls -ls`; correctness is checked by content diffs. It assumes the platform supports sparse file semantics well enough for the mode to run.
