## sources/distributed-fs/eos/namespace/interface/INamespaceGroup.hh

Purpose: Defines an ownership/assembly interface for the full namespace stack: file service, container service, hierarchical view, filesystem view, accounting views, quota stats, stats sink, and cache refresh listener.

Important APIs and types: `initialize` takes a global namespace mutex, config map, error string, and namespace stats. Getters expose file/container services, hierarchical/filesystem views, sync-time accounting, container accounting, quota stats, and in-memory status. `startCacheRefreshListener` starts backend cache invalidation handling.

Control flow: callers construct a concrete namespace group, initialize it, then retrieve service/view pointers and wire MGM operations through them. Startup can fail via boolean/error string.

State and persistence: base class stores non-owning pointers to the global namespace mutex and stats interface. Concrete implementations own persistent/cached namespace components.

Dependencies and integration: depends on namespace stats, common `RWMutex`, metadata services, views, quota stats, and listeners. It is the high-level boundary between MGM and namespace implementation families.

Risks: returned pointers are raw and lifetime is owned by the group implementation. Initialization order matters because services and views depend on each other. Cache refresh listener behavior is backend-specific.

Test signals: initialization success/failure, all getters non-null after init, in-memory flag, listener startup, and teardown/lifetime behavior for concrete groups.
