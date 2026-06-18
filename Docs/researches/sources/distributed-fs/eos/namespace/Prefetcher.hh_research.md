## sources/distributed-fs/eos/namespace/Prefetcher.hh

Purpose: Declares the metadata prefetch engine and its static convenience API for namespace callers.

Important APIs and types: `Prefetcher(IView*)`, stage methods for file/container/item and parent URI resolution, `wait`, and static prefetch helpers for paths, ids, inodes, children, filesystem lists, unlinked lists, and parent paths.

Control flow: header separates manual staging/wait usage from one-shot helpers. Private `prefetchFileUri` and `prefetchContUri` are used for future chaining.

State and persistence: holds raw service/view pointers and vectors of folly futures. No ownership of services is implied.

Dependencies and integration: depends on namespace macros, `IFileMD`, and folly futures; forward-declares services/views. Used broadly by MGM and namespace operations before reading metadata.

Risks: raw `IView*` must outlive the prefetcher and all pending futures. The declared `prefetchContainerMDWithParentsAndWait` takes `IFileMD::id_t` though it represents a container id, which is type-confusing.

Test signals: compile coverage for all overloads, service lifetime assumptions in async tests, and consistency between header declarations and implementation behavior.
