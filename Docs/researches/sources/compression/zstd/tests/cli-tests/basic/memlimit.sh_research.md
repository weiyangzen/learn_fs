# sources/compression/zstd/tests/cli-tests/basic/memlimit.sh

## Purpose

This CLI test validates `--memory`/memory-limit numeric parsing and suffix validation.

## Important APIs, Types, and Functions

It creates `file`, checks invalid suffixes such as `32LB`, `32LiB`, `32A`, random trailing text, and nonnumeric `hello`, then checks accepted suffixes with `1`, `1K`, `1KB`, `1KiB`, `1M`, `1MB`, `1MiB`, `1G`, `1GB`, `1GiB`, `3G`, `3GB`, and `3GiB`. It expects `4G`, `4GB`, and `4GiB` to overflow/reject. `die` reports unexpected results.

## Control Flow, State, and Persistence

The script creates and removes `file` and removes `file.zst` after successful accepted cases. It exits 0 after cleanup.

## Dependencies and Integration Points

It targets `readU32FromCharChecked`, `NEXT_UINT32`, and memory-limit handling in `zstdcli.c`.

## Risks and Test Signals

Main signals are accepted binary suffixes and rejection of trailing garbage or 32-bit unsigned overflow. Cleanup assumes output file name `file.zst`.
