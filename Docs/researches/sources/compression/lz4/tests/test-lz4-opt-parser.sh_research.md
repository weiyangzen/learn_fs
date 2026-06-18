# sources/compression/lz4/tests/test-lz4-opt-parser.sh

## Purpose
This shell test targets compact option parsing for high compression levels and block-size/checksum combinations, especially combined forms such as `-12B4D`, `-11vq`, and `-12BD`.

## Important Control Flow
It streams deterministic `datagen` data of several sizes and probabilities through `lz4` with high-compression options, then pipes to `lz4 -t` or `lz4 -qt` for validation. There is no temporary file state.

## State, Dependencies, and Integration
Dependencies are `datagen`, `lz4`, and the shell pipeline. It integrates with the CLI option parser and high-compression codec modes.

## Risks and Test Signals
The test catches regressions where numeric compression levels, verbosity flags, block sizes, block dependency, and quiet test mode interact incorrectly. It is narrow: success only proves valid streams are produced, not exact compression ratios or parser diagnostics for invalid options.
