# sources/compression/zstd/tests/cli-tests/compression/levels.sh

## Purpose
This CLI regression test validates zstd compression level parsing and level semantics. It checks fast levels, regular levels, `--max`, default level behavior, oversized level rejection, environment-provided `ZSTD_CLEVEL`, and command-line override precedence.

## APIs, control flow, and integration
The script uses the CLI test harness environment where `datagen`, `zstd`, `cmp_size`, and `die` are on `PATH` or sourced by common setup. It generates `file`, captures `zstd -V`, compresses at `--fast=10`, `--fast=1`, `-1`, `-19`, and conditionally `--max`, then validates all outputs with `zstd -t`. Size ordering is asserted with `cmp_size`, and byte equality is asserted with `cmp`. The script then checks aliases/defaults: bare `--fast` must equal `--fast=1`, `-0` must equal default `zstd`, and `-99` must clamp to `-19`.

## State, persistence, dependencies, and risks
All state is scratch-local: `file` and multiple `file-*.zst` outputs. The 32-bit version check avoids `--max` address-space failure by copying the `-19` output. The test depends on deterministic output for identical level options and on generated input being compressible enough for monotonic size comparisons. Risks are platform/version wording in `zstd -V`, future compression tuning changing strict size ordering, and environment leakage; `run.py` normally strips `ZSTD*` variables, but this script intentionally sets `ZSTD_CLEVEL` for individual commands.

## Test signals
Pass signals are successful decompression tests, monotonic compressed sizes, exact output equality for level aliases and env selection, nonzero failure for too-large numeric levels, and command-line level overriding `ZSTD_CLEVEL`.
