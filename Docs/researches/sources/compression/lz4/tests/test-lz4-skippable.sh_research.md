# sources/compression/lz4/tests/test-lz4-skippable.sh

## Purpose
This shell test verifies decoder handling of LZ4 skippable frames using the golden sample `goldenSamples/skip.bin` and a constructed stream containing skippable frames around a valid frame.

## Important Control Flow
It decodes the golden skippable file both as a named file and from stdin. It then compresses a small valid payload, concatenates skippable-valid-skippable, and decodes the combined stream.

## State, Dependencies, and Integration
Temporary output uses the `tmp-lsk` prefix and is removed on EXIT. Dependencies are `lz4`, `printf`, `cat`, and the golden sample. The test integrates with frame decoder logic that must identify and skip skippable frame magic values.

## Risks and Test Signals
This is focused decoder coverage for ignoring skippable data without losing subsequent valid frames. It does not assert exact stdout contents via `cmp`, so regressions that still exit successfully but emit wrong data might be less obvious in automated logs.
