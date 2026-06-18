## sources/cloud-native/moby/daemon/links.go

Purpose: Maintains daemon-level indexes for legacy container link relationships from parent container and alias to child container, plus reverse child-to-parent alias mappings.

Important APIs and types: `linkIndex` holds `idx map[parent]map[alias]child`, `childIdx map[child]map[parent]set(alias)`, and a mutex. `newLinkIndex`, `link`, `unlink`, `children`, `parents`, and `delete` manage the relationship graph.

Control flow and state: `link` initializes nested maps and records both forward and reverse indexes. `unlink` removes a single alias from the parent map and removes the parent entry under the child. `children` returns the stored alias-to-child map for a parent. `parents` builds a fresh alias-to-parent map for a child. `delete` removes all links where the container is parent or child and returns aliases removed from the parent side.

Dependencies and integration points: Uses `daemon/container.Container` pointers as map keys, so identity is object-pointer based. This index supports legacy `--link` behavior and environment/hosts wiring elsewhere in the daemon.

Risks: `children` returns the internal mutable map after releasing the lock, so callers can observe races or mutate index state if misused. `unlink` deletes the entire parent entry under `childIdx[child]`, not just one alias, which is correct only when each parent/child relationship should be removed wholesale. Empty nested maps are not pruned consistently.

Test signals: Separate `daemon/links/links_test.go` covers environment generation, not this index. Direct linkIndex concurrency and alias deletion behavior are not tested in this subset.
