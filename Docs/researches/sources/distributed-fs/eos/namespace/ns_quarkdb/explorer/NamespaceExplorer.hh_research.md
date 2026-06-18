## sources/distributed-fs/eos/namespace/ns_quarkdb/explorer/NamespaceExplorer.hh

Purpose: Declares the QuarkDB namespace exploration API and traversal node type. It provides a higher-level read path for recursively listing namespace items without going through normal mutable services.

Important APIs and types: `ExpansionDecider` is the caller-supplied policy hook for pruning container expansion. `ExplorationOptions` controls depth, expansion filtering, linked-attribute population, link prefixing, optional `IView`, and file suppression. `NamespaceItem` is the returned item union with full path, attrs, file/container flag, metadata proto, expansion-filter state, and direct child counts. `SearchNode` encapsulates async metadata/listing state for one container. `NamespaceExplorer::fetch()` is the public iterator-like API.

State and integration: `NamespaceExplorer` keeps non-owning references to `QClient` and a folly executor, plus DFS state and linked-attribute cache. `SearchNode` owns futures and child nodes, and is a friend-managed implementation detail.

Dependencies: protobuf metadata types, namespace identifiers, `IContainerMD`, `IView`, `FutureVectorIterator`, folly futures, and `QClient`.

Risks and test signals: callers requesting linked attributes must provide `options.view`, or the constructor throws an EOS metadata exception. Returned `NamespaceItem` contains both file and container proto fields but only one is meaningful. Tests should verify option validation, ownership transfer from `SearchNode::expand()`, `canVisit()` behavior when futures fail, and correct child count fields for filtered vs unfiltered containers.
