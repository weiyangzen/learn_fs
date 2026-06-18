# sources/distributed-fs/eos/namespace/ns_quarkdb/NamespaceGroup.hh

Purpose: declares the QuarkDB namespace group implementation of `INamespaceGroup`.

Important APIs/types/functions: public API includes `initialize`, service/view/accounting/quota getters, `isInMemory`, flusher getters, performance monitor getter, qclient getter, executor getter, and `startCacheRefreshListener`. Private members define all owned services and configuration.

Control flow: the header documents that `initialize` must be called before other functions and that the executor must outlive qclient to avoid qclient future continuations referencing a destroyed executor.

State and persistence: owns runtime objects through `std::unique_ptr` and the performance monitor through `std::shared_ptr`; no direct persistence.

Dependencies and integration: implements `INamespaceGroup` contract consumed by the plugin manager and namespace users. Provides central access to QuarkDB backend components.

Risks: many getters return raw pointers into owned members, so consumers must not outlive the group. Recursive mutex allows nested lazy getter calls, but can also hide complex construction cycles.

Test signals: namespace tests instantiate group/services either directly or through plugin-like setup.
