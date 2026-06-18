## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/evlist.h

Purpose: Defines the internal libperf event-list structure, mmap callback interface, iteration macros, and internal helper declarations.

Important APIs/types: `struct perf_evlist` contains evsel entries, CPU/thread maps, mmap state, fdarray poll state, and sample-ID hash heads. `struct perf_evlist_mmap_ops` abstracts mmap allocation and mapping callbacks. Macros iterate entries forward, reverse, and safely.

Control flow: Inline `perf_evlist__first/last()` and iteration macros drive many evlist operations. Mmap ops callbacks let tests or alternate implementations hook mapping behavior.

State/persistence: Defines in-memory ownership fields for evlist runtime; no storage by itself.

Dependencies/integration: Includes Linux list, fdarray, internal cpumap/evsel. Used by evlist implementation and internal tests.

Risks: `perf_evlist__first/last()` assume non-empty lists. Hash size constants tune sample-ID lookup. Internal fields are exposed to installed internal-header consumers.

Test signals: Compile internal users, exercise iteration macros on empty/non-empty lists, and validate mmap callback hooks in tests.
