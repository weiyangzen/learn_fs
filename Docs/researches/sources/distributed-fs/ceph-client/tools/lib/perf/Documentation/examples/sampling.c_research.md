## sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/examples/sampling.c

Purpose: Demonstrates libperf sampling mode over online CPUs using an mmaped perf ring buffer.

Important APIs/functions: Uses `perf_cpu_map__new_online_cpus()`, evlist/evsel setup, `perf_evlist__mmap()`, enable/sleep/disable, `perf_evlist__for_each_mmap()`, `perf_mmap__read_init()`, `perf_mmap__read_event()`, `perf_mmap__consume()`, and `perf_mmap__read_done()`.

Control flow: Main creates a hardware CPU cycles sampling event at frequency 10 with IP/TID/CPU/PERIOD sample fields. After opening and mmaping, it samples for three seconds, then iterates mmap buffers, decodes raw sample arrays in the declared sample order, prints fields, and consumes events.

State/persistence: Runtime perf FDs, CPU map, evlist, mmap ring buffers. No persistent storage.

Dependencies/integration: Depends on public libperf mmap/event APIs and kernel perf sampling permissions/hardware PMU support.

Risks: Raw sample decoding assumes the exact sample_type order and native layout. Hardware cycles may be unavailable in containers or restricted by `perf_event_paranoid`. Cleanup path on evsel creation failure jumps to `out_cpus` via `out_cpus`/`out_evlist` and should be checked for evlist leaks in edits.

Test signals: Build and run with adequate permissions, verify samples decode without overruns, test no-PMU/restricted-permission failures, and validate mmap cleanup with sanitizers.
