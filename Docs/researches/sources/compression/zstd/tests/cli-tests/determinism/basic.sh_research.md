# sources/compression/zstd/tests/cli-tests/determinism/basic.sh

## Purpose
This test locks single-threaded compression determinism across levels, long-distance settings, and fast mode by comparing md5 hashes against harness expectation files.

## APIs, control flow, and integration
After sourcing platform helpers, it skips by replaying the exact expected stdout if `NON_DETERMINISTIC` is set. Otherwise it loops levels 1 through 19 over `files/*`, prints a stable label, pipes `zstd --single-thread -q -$level ... -c` to `md5hash`, then covers `--long=18` at levels 1 and 19 and `--fast=1`.

## State, dependencies, risks, and test signals
It reads the `files` directory produced by setup and writes no durable outputs. Dependencies include deterministic `datagen` fixtures, `seq`, `ls`, `md5hash`, and exact stdout files. Risks are intentional compression format/tuning changes requiring golden hash updates. Pass confirms byte-for-byte reproducibility for the selected matrix.
