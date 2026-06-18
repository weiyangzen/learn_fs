# sources/distributed-fs/ceph-client/include/trace/events/page_ref.h

Purpose: Defines trace classes for page reference-count modifications. It enables low-level debugging of page/folio lifetime bugs.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(page_ref_mod_template)` underlies `page_ref_set`, `page_ref_mod`, and `page_ref_unfreeze`. `DECLARE_EVENT_CLASS(page_ref_mod_and_test_template)` underlies `page_ref_mod_and_test`, `page_ref_mod_and_return`, `page_ref_mod_unless`, and `page_ref_freeze`. Fields include page pointer, PFN, flags, count, mapcount, mapping, mt, val, and return value.

Control flow: Page reference helpers emit events when setting, incrementing/decrementing, freezing, unfreezing, or conditionally modifying counts. The tracepoint snapshots page identity and counters around the atomic operation.

State and persistence: The header owns no state. It observes page/folio refcounts and mapping metadata that control physical page lifetime.

Dependencies and integration points: Depends on `linux/page_ref.h`, MM flags, tracepoints, and memory-management internals. It integrates with debug configs and page lifetime tracing.

Risks and test signals: Risks include high overhead on ubiquitous refcount paths, reading page metadata while it changes, and traces that are hard to interpret after page reuse. Test page_ref debug builds, folio allocation/free, migration, GUP, page cache, slab-backed pages where applicable, and leak/use-after-free investigations.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/page_ref.h` completely for this pass (135 lines, 3058 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/page_ref.h_research.md`.
