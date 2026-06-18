# sources/compression/zstd/tests/cli-tests/determinism/multithread.sh

## Purpose
This test checks deterministic output for multi-threaded compression and verifies that varying thread counts does not change selected outputs for representative inputs.

## APIs, control flow, and integration
It skips by replaying expected stdout when `NON_DETERMINISTIC` is set or `$hasMT` is empty. Otherwise it hashes `zstd -T2` output for levels 1, 3, 7, and 19 across `files/*`, hashes long-distance output at levels 1 and 19, then creates a single-thread reference for each file and compares `-T1`, `-T2`, and `-T4` outputs with `$DIFF`.

## State, dependencies, risks, and test signals
State includes temporary `*.zst` and `*.zst.good` files under the copied `files` directory. Dependencies are thread-enabled zstd, platform helper variables, and exact stdout fixtures. Risks are legitimate multi-thread format changes and CPU/thread availability differences. Pass confirms deterministic frame bytes across fixed multi-thread settings and thread-count equivalence for the tested level.
