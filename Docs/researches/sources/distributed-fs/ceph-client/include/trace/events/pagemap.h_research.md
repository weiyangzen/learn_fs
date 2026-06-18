# sources/distributed-fs/ceph-client/include/trace/events/pagemap.h

Purpose: Provides tracepoints for LRU insertion and activation in the page cache and memory-management pagemap layer.

Important APIs/types/functions: `mm_lru_insertion` records page/folio pointer, PFN, lru flag state, and whether the insertion is file or anon. `mm_lru_activate` records page/folio activation metadata.

Control flow: MM code emits insertion when pages enter an LRU list and activation when reclaim/access logic promotes pages. Trace fast assignment snapshots flags and mapping-related state.

State and persistence: No state is stored by the header. It observes folio/page LRU state in memory; persistence is only the page cache and backing memory state outside tracing.

Dependencies and integration points: Depends on `linux/mm.h` and tracepoints. It integrates with page cache, reclaim, workingset detection, and memory-pressure diagnostics.

Risks and test signals: Risks include excessive event volume, folio/page terminology drift, flag interpretation errors, and tracing pages during migration or free. Test page cache workloads, anonymous memory pressure, reclaim/activation behavior, memcg pressure, and LRU transitions with tracing enabled.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pagemap.h` completely for this pass (83 lines, 2190 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pagemap.h_research.md`.
