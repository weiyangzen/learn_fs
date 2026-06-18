# sources/compression/zstd/tests/cli-tests/compression/row-match-finder.sh

## Purpose
This script tests option parsing and successful compression for the row match finder toggle.

## APIs, control flow, and integration
It assumes `file` exists and runs `zstd file -7f --row-match-finder` followed by `zstd file -7f --no-row-match-finder`. The `-7` level selects a strategy where the row match finder option is relevant; `-f` allows overwriting `file.zst`.

## State, dependencies, risks, and test signals
The test only checks command success, not output equality or ratio. It depends on the build exposing both options. The risk is limited coverage: parser acceptance and no crash are tested, while algorithmic selection is inferred from the CLI path.
