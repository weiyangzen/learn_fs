# sources/distributed-fs/ceph-client/tools/perf/util/probe-file.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/probe-file.h` declares the tracefs probe-file and probe-cache API implemented by `probe-file.c`. It provides the in-memory cache entry/container shapes and a compile-time feature boundary for builds without libelf support.

## Important APIs, Types, and Functions

The key types are `struct probe_cache_entry`, containing an SDT flag, copied `perf_probe_event`, synthesized perf command, and trace-event string list, and `struct probe_cache`, containing the cache fd and list of entries. `enum probe_type` names tracefs type suffix capabilities. Flags `PF_FL_UPROBE` and `PF_FL_RW` select uprobe and writable open modes. `for_each_probe_cache_entry` wraps list iteration.

When `HAVE_LIBELF_SUPPORT` is available, the header declares probe-file open/list/add/delete functions, cache lookup/update/commit/show functions, SDT scanning, and tracefs feature capability checks. Without libelf, only stubbed `probe_cache__new` and `probe_cache__delete` are provided.

## Control Flow

The header has no runtime flow. Callers use it to open tracefs files, inspect existing probes, add or delete trace events, load or mutate cache entries, and query tracefs syntax support before generating commands.

## State and Persistence Behavior

It defines ownership of cache entry members but does not allocate state itself. Persistent behavior is delegated to the implementation and the build-id cache `probes` files.

## Dependencies and Integration Points

It includes `probe-event.h` and forward-declares `strlist` and `strfilter`. It integrates probe cache operations with higher-level `perf probe` command code and SDT users. The libelf guard lets the rest of perf compile in reduced configurations while disabling cache-heavy operations.

## Risks and Edge Cases

Callers must respect the libelf guard; most APIs disappear when libelf is disabled. Cache entry lifetime is nontrivial because nested events, strings, and lists are owned by the implementation. `probe_type` availability is not purely compile-time and must be queried at runtime.

## Test Signals

Compile tests with and without `HAVE_LIBELF_SUPPORT`, API users that exercise both kprobe and uprobe flag modes, cache iteration tests, and feature-gated command synthesis tests are the strongest signals.
