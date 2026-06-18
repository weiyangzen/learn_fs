## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/mmap.h

Purpose: Defines internal perf mmap ring-buffer state and operations.

Important APIs/types: `PERF_SAMPLE_MAX_SIZE`, `libperf_unmap_cb_t`, `struct perf_mmap`, `struct perf_mmap_param`, and declarations for init/mmap/munmap/get/put/read-head/read-self helpers.

Control flow: Runtime users initialize a `perf_mmap`, map a perf FD with parameters, read head/self counts, consume elsewhere, and release via refcounted get/put or munmap.

State/persistence: `struct perf_mmap` tracks base pointer, mask, fd, CPU, refcount, read positions, overwrite mode, flush state, event-copy buffer, and linked `next` pointer.

Dependencies/integration: Used by evlist/evsel mmap paths and public mmap APIs. Depends on refcount, Linux types, CPU map type, and perf count values.

Risks: Ring-buffer correctness depends on mask/page-size setup and refcount lifecycle. `event_copy` handles wrapped samples and must respect `PERF_SAMPLE_MAX_SIZE`.

Test signals: Mmap read/consume tests for forward and overwrite buffers, refcount get/put balance, wrapped events, self-read counts, and unmap callbacks.
