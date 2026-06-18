# Research: sources/distributed-fs/ceph-client/tools/perf/bench/inject-buildid.c

Purpose: benchmarks `perf inject -b` and `perf inject -b --buildid-all` by synthesizing perf.data streams with MMAP2 and SAMPLE events referencing real DSOs with build IDs.

Important APIs/types/functions: `bench_inject_build_id()` runs the benchmark. `collect_dso()` walks `/usr/lib` via `nftw()` and `add_dso()` to collect DSOs with build IDs. `setup_injection()` forks a child that runs perf's `main()` as `perf inject`. `synthesize_attr()`, `synthesize_fork()`, `synthesize_mmap()`, `synthesize_sample()`, and `synthesize_flush()` write input records. `inject_build_id()` feeds one iteration and collects child `ru_maxrss`.

Control flow: after option parsing, symbol support initializes, sample type/header size are fixed, DSOs are collected, then two loops run: build-id injection and build-id-all injection. Each iteration creates pipes, forks perf inject, writes a perf pipe header, attr/fork records, randomized mmap/sample records, periodic finished-round records, closes input, waits for child, joins output drain thread, and updates timing/memory stats.

State and persistence: process-local arrays store DSO paths and inode ids; pipes connect parent and child. No benchmark output files are persisted, but it reads real filesystem DSOs and executes an in-process child perf command.

Dependencies and integration: depends on perf data/header/session/sample/synthetic event APIs, build-id reading, symbol init, pthreads, fork/pipe/wait4, `/usr/lib` contents, and perf's top-level `main()`.

Risks: assumes enough DSOs with build IDs under `/usr/lib`; otherwise benchmark cannot run. Forking and calling `main()` recursively is unusual and sensitive to global state. Large path names require split writes around sample id headers. Child stderr is redirected to `/dev/null`, hiding diagnostics.

Test signals: systems with/without build-id DSOs, varied mmap/sample/iteration counts, verbose DSO collection, child exit status, memory usage stability, and comparison of `-b` versus `--buildid-all`.
