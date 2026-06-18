# sources/compression/lz4/tests/test_custom_block_sizes.sh

## Purpose
This shell test validates custom `-B<size>` parsing and mapping to LZ4 frame block-size IDs. It verifies lower-bound rejection and expected block descriptor classes for sizes spanning all supported ranges.

## Important Control Flow
It creates two deterministic input files in `/tmp`, expects `-B31` to fail, then loops over ranges that should map to `b4`, `b5`, `b6`, and `b7`. For each size it compresses both inputs, concatenates the frames, and runs `checkFrame -B<effective-size> -b<id>` to validate headers. A `failures` string accumulates failing block sizes and determines exit status.

## State, Dependencies, and Integration
State is `/tmp/test_custom_block_sizes*`. Dependencies are `../lz4`, `./checkFrame`, `./datagen`, `cat`, and shell loops. It integrates with CLI parsing and the frame checker utility.

## Risks and Test Signals
The test is strong for boundary values like 65535/65536/65537 and for clamping above 4 MiB. Cleanup is manual at the end, so an early failure under `set -e` can leave `/tmp` artifacts. It assumes fixed relative paths from the tests directory.
