# Research: sources/cloud-native/moby/daemon/libnetwork/internal/maputil/maputil.go

Purpose: provides a generic helper for filtering map values. Important API is `FilterValues[K comparable, V any]`.

Control flow: the function iterates all map values, applies the predicate, and appends matching values to a slice. It returns nil or an empty slice depending on whether any append occurs and does not preserve any deterministic order because Go map iteration is randomized.

State/dependencies: no state or external dependencies. Integration point in this subset is `Controller.findEndpoints`, which filters the controller endpoint cache by network ID. Risks include callers assuming stable ordering or copies; the helper returns the original values. It performs no locking, so callers must guard the input map if concurrent writes are possible. Test signal is indirect via endpoint store tests.
