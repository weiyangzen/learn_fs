## sources/cloud-native/moby/daemon/list.go

Purpose: Implements daemon container listing (`docker ps`) by validating filters, building a reusable filter context, selecting candidate containers, applying list predicates, refreshing image display data, optionally computing sizes, and returning ordered `container.Summary` values.

Important APIs and types: `acceptedPsFilterTags` defines allowed filters. `iterationAction` controls include/exclude/stop. `(*Daemon).List` returns all registered containers. `listContext` stores folded filters: names, images, exited codes, before/since snapshots, task/is-task flags, publish/expose maps, and original `ContainerListOptions`. Key functions are `(*Daemon).Containers`, `filterByNameIDMatches`, `foldFilter`, `idOrNameFilter`, `portOp`, `includeContainerInList`, `refreshImage`, and `populateImageFilterByParents`.

Control flow and state: `Containers` validates filters, snapshots the container view, folds filters, optionally narrows candidates by name/ID, sorts by creation time, and launches an errgroup with `log2(n)` worker limit. Each included container is assigned a stable result index before goroutine processing, preserving output order. `includeContainerInList` implements before/since, stopped/all/limit, name/id, task, label, isolation, exit/status/health, volume, ancestor, network, publish, and expose checks. `refreshImage` replaces stale image references with the original image ID if the reference no longer resolves to the stored image ID.

Dependencies and integration points: Integrates with `container.ViewDB`, daemon name reservation, image service (`GetImage`, `Children`, layer size), filters package, API container/network types, platform-specific `excludeByIsolation`, and errdefs.

Risks: Filter semantics are broad and order-dependent. `filter.idx` is mutated while goroutines run, but only the main loop mutates it; results use a mutex. Ancestor expansion recursively walks image children and can be expensive. Size calculation can dominate latency and returns errors for individual container layer failures. Name/ID shortcut must remain consistent with full-list filtering.

Test signals: `list_test.go` covers invalid filter validation, creation-order listing across several counts, name filter slash/regex behavior, and limit semantics. Many filters are not covered in this subset.
