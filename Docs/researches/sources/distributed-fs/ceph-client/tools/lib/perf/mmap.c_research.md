<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/mmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/mmap.c

## Purpose
This file implements libperf mmap ring-buffer setup, teardown, event iteration, overwrite-buffer handling, refcounted unmapping, and user-space counter reads from perf mmap pages.

## Important APIs, Types, and Functions
- `perf_mmap__init` initializes fd, overwrite flag, optional unmap callback, refcount, and linked-list `next`.
- `perf_mmap__mmap_len` returns `mask + 1 + page_size`.
- `perf_mmap__mmap` maps the perf fd with `mmap`, stores fd/cpu/mask, and resets `prev`.
- `perf_mmap__munmap`, `get`, and `put` handle event-copy storage, `munmap`, fd reset, refcount reset, and callback dispatch.
- `perf_mmap__consume` writes the ring tail for non-overwrite mode and auto-puts the last reference when empty.
- `perf_mmap__read_init`, `read_event`, and `read_done` implement public event traversal.
- `overwrite_rb_find_range` recovers readable ranges in full backward overwrite buffers.
- Architecture-specific `read_perf_counter` and `read_timestamp` support x86, arm64, riscv64, and fallback paths.
- `perf_mmap__read_self` reads counts directly from the mmap page using seq-lock style validation, rdpmc/PMU registers, and time scaling.

## Control Flow and State
The ring state is `prev`, `start`, `end`, `mask`, `flush`, `overwrite`, `base`, and a temporary `event_copy` for records that wrap across the buffer end. Non-overwrite mode advances `prev` as events are read and writes it to kernel tail on consume. Overwrite mode snapshots head/start/end and requires `read_done` to reset `prev` to the latest head. Refcount zero indicates an unmapped/hung-up event.

## Dependencies and Integration Points
It depends on perf mmap public/internal headers, Linux ring-buffer helpers, perf_event mmap-page layout, kernel math/barrier helpers, and `page_size` from `lib.c`. Evsel/evlist mmap APIs create `struct perf_mmap` instances and tests consume them through `perf/mmap.h`.

## Risks and Test Signals
The highest-risk areas are wraparound copy logic, overwrite full-buffer recovery, memory-ordering around mmap-page lock/head fields, architecture-specific counter register mapping, and lifecycle interactions between poll hangups and refcounts. `test-evlist.c` validates tracepoint ring-buffer consumption by generating `prctl` events; `test-evsel.c` validates mmap base access and user counter reads on supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/mmap.c -->
