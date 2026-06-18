# sources/compression/lz4/tests/test-lz4-multiple-legacy.sh

## Purpose
This shell test validates multi-file mode with legacy LZ4 format enabled by `-l`. It checks one-output-per-input behavior, stdout concatenation behavior, decompression behavior, and partial failure handling.

## Important Control Flow
The script generates three inputs, compresses with `lz4 -f -l -m`, verifies `.lz4` artifacts, restores originals from compressed files, and compares with `cmp`. It then compares concatenated individual compressed files with `lz4 -l -m ... -c`, and verifies decompression of multiple legacy files to stdout. A final command includes a missing file and expects failure while confirming later valid outputs may still be created.

## State, Dependencies, and Integration
State is `tmp-lml*`; dependencies are `datagen`, `lz4`, `cat`, `cmp`, `rm`, and shell globbing. It integrates with CLI multi-file dispatch, legacy frame codec selection, and error aggregation.

## Risks and Test Signals
The test confirms `-l` does not interfere with `-d` behavior and that `-c` suppresses file artifact creation. It is sensitive to shell glob ordering and to any change in the policy for whether multi-file processing continues after non-blocking errors.
