# sources/compression/lz4/tests/test-lz4hc-hugefile.sh

## Purpose
This minimal shell test exercises high-compression mode on a multi-gigabyte stream. It streams 4200 MB from `datagen` through `lz4 -v3` and validates with `lz4 -qt`.

## Important Control Flow
There is no temporary file state; the test is a single pipeline under `set -e` and `set -x`.

## State, Dependencies, and Integration
Dependencies are `datagen`, `lz4`, and a host capable of processing a 4.2 GB stream. It integrates with high-compression streaming and test-mode decoding.

## Risks and Test Signals
The signal targets large-size counters and high-compression stability. It is resource-heavy but disk-light because the data remains in a pipeline. It does not compare output ratios or persist artifacts for inspection.
