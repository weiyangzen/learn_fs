## sources/distributed-fs/eos/namespace/ns_quarkdb/explorer/NamespaceExplorer.cc

Purpose: Implements recursive namespace exploration over QuarkDB metadata, primarily for find-like commands. It walks from a requested path, yields containers and files, optionally counts children, filters expansion, and resolves linked attributes.

Important APIs and control flow: `SearchNode` starts async fetches for container metadata and child container maps. `handleAsync()` stages child containers when ready and either starts a file listing or a file-count query depending on `ignoreFiles`/filtering. `expand()` validates parent expectations, stages sorted children, and returns the next child node by ownership transfer. `fetchChild()` drains `FutureVectorIterator<FileMdProto>`, swallowing `MDException`s in a retry loop. `NamespaceExplorer` constructor resolves the static path synchronously; if the last path component is not a container, it may resolve it as a single file. `fetch()` emits a single file search result, or performs DFS: visit container, run expansion decider/depth limit, yield file children, expand subcontainers, then pop exhausted nodes.

State and persistence behavior: the explorer is read-only and has no consistency guarantees against pending flusher writes. It stores a static path, a DFS stack, cached linked attributes keyed by link target, and per-node futures for metadata, maps, file lists, and counts.

Dependencies and integration: uses `MetadataFetcher`, `PathProcessor`/`SplitPath`, `Attributes::populateLinkedAttributes`, `IView::getItem()` for linked attrs, folly futures/executors, and EOS path utilities.

Risks and test signals: `depthLimit` defaults to zero and is compared with `>=`, so callers must understand whether zero means no recursion or root-only behavior. `fetchChild()` catches `MDException` and loops, which could spin if the iterator repeatedly throws. Full path generation is rebuilt on every fetch. Tests should cover file-vs-container path resolution, sorted child order, parent mismatch warning, expansion filtering, linked-attribute cache behavior, ignore-files counts, and depth-limit semantics.
