# sources/distributed-fs/ceph-client/drivers/block/zram/zcomp.c

Purpose: dynamic compression frontend for zram. It registers configured backend ops, allocates per-CPU compression streams, handles CPU hotplug, and exposes compressor lookup/availability helpers.

Important APIs/types/functions: `backends[]` is the conditional backend registry. `lookup_backend_ops()`, `zcomp_lookup_backend_name()`, and `zcomp_available_show()` serve sysfs/config selection. `zcomp_strm_init()` and `zcomp_strm_free()` create backend contexts plus page-sized scratch buffers. `zcomp_stream_get()`/`put()` lock a per-CPU stream safely across CPU hotplug. `zcomp_compress()` and `zcomp_decompress()` wrap backend ops. `zcomp_create()`, `zcomp_init()`, and `zcomp_destroy()` manage full compressor lifetime.

Control flow: create validates backend name, allocates `struct zcomp`, sets ops, allocates per-CPU streams, lets the backend setup immutable params, initializes stream locks, and registers a CPU hotplug instance. CPU-up initializes streams; CPU-dead frees them under the stream lock. Compression gets a locked stream, builds a `zcomp_req` for one page and a two-page output buffer, and delegates to the backend.

State and persistence: per-device `zcomp_params` are shared and backend-owned `drv_data` may persist for the compressor lifetime. Per-CPU `zcomp_strm` contains mutable backend context, compressed buffer, and local copy buffer. Stream `buffer == NULL` marks a stream destroyed during CPU hotplug and makes `zcomp_stream_get()` retry after migration.

Dependencies and integration: depends on all enabled backend headers, cpuhp state `CPUHP_ZCOMP_PREPARE`, vmalloc, sysfs formatting, mutexes, and zram driver callers.

Risks: backends must implement setup/release/create/destroy consistently or hotplug cleanup can leak or double-free. `zcomp_stream_get()` loops until it lands on a live CPU stream; CPU hotplug races are handled by lock and NULL-buffer retry. The two-page compression buffer assumes zram handles incompressible pages outside the backend.

Test signals: backend lookup with sysfs-style strings, available compressor formatting, create/destroy under each backend, CPU hotplug online/offline, compression/decompression round trips, backend setup failure cleanup, and concurrent stream users.
