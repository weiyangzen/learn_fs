# sources/compression/lz4/tests/test-lz4-frame-concatenation.sh

## Purpose
This shell test confirms that `lz4 -d` decodes concatenated LZ4 frames, including an empty frame between non-empty frames, into the concatenation of their original payloads.

## Important Control Flow
It creates empty and non-empty source files, builds a reference concatenation, compresses each source independently, concatenates the compressed frames, decodes the combined stream to a result file, and compares with `cmp`.

## State, Dependencies, and Integration
State is limited to `tmp-lfc*` files. Dependencies are `lz4`, `cat`, `cmp`, and POSIX shell behavior. The test integrates with frame decoder stream traversal and EOF handling.

## Risks and Test Signals
The signal is narrow and valuable: decoders must continue after each complete frame and not mishandle zero-length frames. It does not cover skippable or legacy frames; those are handled by other tests in this subset.
