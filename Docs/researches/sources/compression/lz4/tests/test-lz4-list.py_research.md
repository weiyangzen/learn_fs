# sources/compression/lz4/tests/test-lz4-list.py

## Purpose
This Python unittest validates `lz4 --list` output for single-frame, multi-frame, legacy, skippable, content-size, checksum, and block-mode cases. It constructs a controlled corpus in the system temp directory and checks both non-verbose and verbose list formats.

## Important APIs and Control Flow
`NVerboseFileInfo` parses the seven-column non-verbose rows and computes expected compressed/uncompressed sizes. `VerboseFileInfo` parses per-frame verbose rows. `execute()` wraps subprocess calls, optionally prepending `QEMU_SYS`. `generate_files()` creates sparse-ish random test payloads, LZ4 frames with options such as `--content-size`, `-BI`, `-BD`, `-BX`, `--no-frame-crc`, hand-written skippable frames, legacy frames, and concatenated files. Two unittest classes assert frame counts, types, block descriptors, checksums, ratios, and human-readable sizes.

## State, Dependencies, and Integration
State is `/tmp/test_list*` and is removed before and after the run. Dependencies include Python `unittest`, `tempfile`, `glob`, `os.urandom`, and the built `lz4` binary from either `../lz4` or `../programs/lz4`. It directly tests CLI presentation and parser-visible frame metadata.

## Risks and Test Signals
This is strong output-format regression coverage, but brittle because it parses whitespace-delimited CLI output and assumes filenames without spaces. One assertion in verbose block testing compares against the literal regex string for `--BI`, which may be intentional legacy behavior or a test typo. Random payloads make sizes deterministic only in aggregate expectations, not by content.
