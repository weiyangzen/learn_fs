# sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/io-stats-mem-types.h

## Purpose
Defines memory-accounting type IDs for allocations made by the `debug/io-stats` translator.

## Important APIs, types, and functions
The `gf_io_stats_mem_types_` enum starts at `gf_common_mt_end + 1` and defines tags for `ios_conf`, `ios_fd`, `ios_stat`, `ios_stat_list`, `ios_sample_buf`, `ios_sample`, and the sentinel `gf_io_stats_mt_end`. It also declares `extern const char *__progname`, which `io-stats.c` uses when forming dump filenames.

## Control flow
`mem_acct_init()` in `io-stats.c` passes `gf_io_stats_mt_end` to `xlator_mem_acct_init()`. Allocation sites then use the specific tags with `GF_CALLOC()` or related allocation helpers.

## State and persistence behavior
The enum does not hold runtime state. It affects in-memory accounting and diagnostics only.

## Dependencies and integration points
Includes `glusterfs/mem-types.h` for the shared memory-type base. Integrated with GlusterFS memory accounting and the module build.

## Risks and test signals
Adding allocation categories requires keeping the enum before the sentinel and ensuring `mem_acct_init()` still covers all tags. Tests should include memory-accounting initialization and leak diagnostics for the io-stats translator.
