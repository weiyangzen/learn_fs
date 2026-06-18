# sources/distributed-fs/glusterfs/libglusterfs/src/statedump.c

## Purpose

`statedump.c` implements Gluster's process statedump facility. It parses statedump option files, writes diagnostic sections and key/value pairs to either a temporary dump file or a `strfd_t`, gathers memory, mempool, dictionary, callpool, graph, translator, inode/fd, and latency information, and atomically renames completed dump files into the configured statedump directory.

## Important APIs, Types, and Functions

Public writers are `gf_proc_dump_add_section()` and `gf_proc_dump_write()`. Diagnostic APIs include `gf_proc_dump_info()`, `gf_proc_dump_mem_info()`, `gf_proc_dump_mem_info_to_dict()`, `gf_proc_dump_mempool_info()`, `gf_proc_dump_mempool_info_to_dict()`, `gf_proc_dump_dict_info()`, `gf_proc_dump_xlator_private()`, `gf_proc_dump_mallinfo()`, `gf_proc_dump_xlator_history()`, `gf_proc_dump_xlator_itable()`, `gf_proc_dump_xlator_meminfo()`, and `gf_proc_dump_xlator_profile()`. Lifecycle functions are `gf_proc_dump_init()`, `gf_proc_dump_fini()`, and `gf_proc_dump_cleanup()`. Global state includes `gf_proc_dump_mutex`, `gf_dump_fd`, `dump_options`, and `gf_dump_strfd`.

## Control Flow and Data Flow

`gf_proc_dump_info()` is the main dump path. It validates context, optionally locks `cleanup_lock` for multiplexed daemons, takes the dump mutex, determines brick naming and dump options, creates a temporary file with restrictive umask, writes start time, dumps mempools, iobuf stats, pending frames, dictionary stats, root translator info, active graph info, and old graph info, writes end time, closes the file, and renames the temp path to the final dump path. Option parsing first checks process-specific and global option files under the runtime directory, handles custom `path=`, enables all options by default when no options file exists, and falls back to default mem/callpool if everything is disabled.

The string-output APIs set `gf_dump_strfd` under the dump mutex, call the relevant dump operation, and reset it. Writer helpers choose fd output or string-buffer output based on that global pointer.

## State and Persistence Behavior

The primary persistent artifact is a dump file named from brick/process/time under `dump_options.dump_path`, `ctx->statedump_path`, or `DEFAULT_VAR_RUN_DIRECTORY`. It is written through `mkstemp()` and published by `sys_rename()`. In-memory dump state is process-global and protected by `gf_proc_dump_mutex`. Latency dumps reset per-FOP latency accumulators after writing.

## Dependencies and Integration Points

This file depends on logging, statedump declarations, syscall wrappers, optional `mallinfo`/`mallinfo2`, mempool lists, iobuf stats, callpool dumping from `stack.c`, translator dumpops, graph lists, management multiplexing helpers, `strfd.c`, dictionary setters, and time formatting. It is invoked by SIGUSR1 or management paths and is used by operational diagnostics.

## Risks and Edge Cases

The header explicitly avoids normal `gf_log` inside some dump paths because statedump can be signal-driven and lock-sensitive. `gf_proc_dump_dict_info()` divides by `total_dicts` without checking zero in the observed code, so empty counters are risky. Option parsing reads whitespace-delimited `key=value` tokens and ignores malformed tokens. String-output mode relies on one global pointer, so the dump mutex is mandatory. Failure to close or rename the temp file leaves an unpublished dump. Old graph and active graph traversal must tolerate concurrent cleanup, especially in multiplexed daemons.

## Test Signals

Tests should cover default/no option files, process-specific options, global options, custom dump paths, disabled-all fallback, malformed keys, temp-file rename, restrictive file permissions, string-backed dump APIs, latency reset, and active/old graph traversal. Concurrency tests should trigger statedump during translator cleanup and while locks are held, verifying nondeadlock and partial-dump behavior.
