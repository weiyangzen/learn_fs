# sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/toleration.go

## Purpose
`toleration.go` implements a deterministic set abstraction for Kubernetes tolerations.

## Important APIs, Types, and Functions
`TolerationSet` stores tolerations in a map keyed by `getKey`, which concatenates key, operator, effect, and value. `Add` initializes the map if needed and stores/replaces by key. `ToList` returns all tolerations sorted by the same key for stable output.

## Control Flow, State, and Persistence
State is in-memory. Adding the same logical toleration overwrites the existing entry, and `ToList` creates a sorted slice without mutating Kubernetes objects directly.

## Dependencies and Integration Points
It depends on `corev1.Toleration` and is intended for disruption/controller configuration paths that need stable toleration lists for pod specs or controller options.

## Risks
The key excludes `TolerationSeconds`, so two tolerations that differ only by duration collide and the later one wins. `ToList` on a zero-value set returns an empty slice, which is safe. There is no locking, so callers should not mutate one set concurrently.

## Test Signals
No direct tests are in this subset. Good signals would cover duplicate elimination, deterministic ordering, and the `TolerationSeconds` collision behavior if duration-sensitive tolerations are expected.
