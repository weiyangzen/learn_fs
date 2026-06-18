# sources/distributed-fs/ceph-client/include/trace/events/vmalloc.h

Purpose: Instruments vmap area allocation, lazy purge, and no-flush free activity in the vmalloc allocator.

Important APIs/types/functions: Defines `alloc_vmap_area`, `purge_vmap_area_lazy`, and `free_vmap_area_noflush`, exposing virtual address range, size/alignment, requested address window, caller return address, and purge/free counters.

Control flow: vmalloc/vmap code emits allocation/free/purge events as vmap areas move through allocator paths. TP assignments snapshot scalar range metadata.

State/persistence: Vmap areas remain managed by vmalloc internals. The trace stream provides persistent allocator observations.

Dependencies/integration: Includes tracepoint infrastructure and vmalloc internal callers; consumed by MM fragmentation and leak diagnostics.

Risks: Address and caller fields may be sensitive in production traces. Field changes can break scripts that monitor vmalloc pressure.

Test signals: Exercise vmalloc/vfree/module-load paths with `vmalloc:*` enabled and verify allocation/free pairing and purge counts.
