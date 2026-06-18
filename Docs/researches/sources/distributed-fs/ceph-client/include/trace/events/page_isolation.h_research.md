# sources/distributed-fs/ceph-client/include/trace/events/page_isolation.h

Purpose: Defines a tracepoint for page-isolation checks used by memory offlining, compaction, and page migration diagnostics.

Important APIs/types/functions: `test_pages_isolated` records a PFN range, isolated start/end PFNs, and the result of an isolation test.

Control flow: Memory isolation code emits the event after testing whether a range can be isolated. It captures both requested and actually isolated spans to explain failures or partial isolation.

State and persistence: No state is owned. It observes zone/pageblock isolation state and page migration conditions in memory-management code.

Dependencies and integration points: Depends on tracepoints and integrates with memory hotplug, CMA, compaction, alloc_contig_range, and page migration workflows.

Risks and test signals: Risks include PFN range off-by-one errors, missing context for why a page failed isolation, and hotplug races. Test memory offline/online, CMA allocation, gigantic page allocation, movable/unmovable page ranges, and isolation failure injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/page_isolation.h` completely for this pass (39 lines, 943 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/page_isolation.h_research.md`.
