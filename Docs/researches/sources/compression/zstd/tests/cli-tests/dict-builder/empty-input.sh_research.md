# sources/compression/zstd/tests/cli-tests/dict-builder/empty-input.sh

## Purpose
This dictionary-builder test verifies that training handles an empty sample alongside valid samples.

## APIs, control flow, and integration
It generates 50 files with seeds 1 through 50, creates an empty file with `touch empty`, enables verbose shell tracing, and runs `zstd -q --train empty file*`. The command is expected to succeed.

## State, dependencies, risks, and test signals
Scratch state is the generated sample set, the empty file, and default dictionary output side effects. Dependencies are `datagen`, `seq`, and dictionary trainer support. Risks include sample glob ordering and future stricter trainer validation. A pass confirms empty input samples are ignored or handled without fatal errors.
