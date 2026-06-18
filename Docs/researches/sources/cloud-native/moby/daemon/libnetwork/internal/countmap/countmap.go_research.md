# Research: sources/cloud-native/moby/daemon/libnetwork/internal/countmap/countmap.go

Purpose: defines a generic map-of-counters helper. Important type/API is `Map[T comparable]` with method `Add`.

Control flow: `Add` increments the counter for key `v` by `delta`, returns the new value, and deletes the key when the new count is zero. It allows negative counts and does not enforce non-negative reference semantics.

State/dependencies: state is the caller-owned Go map; there is no locking or persistence. Dependencies are only Go generics and comparable keys. Integration points are places needing compact reference counts without retaining zero entries. Risks include nil map panics when adding to an uninitialized nil map, no synchronization, and negative count semantics being caller-dependent. Tests verify positive, negative, and zero-removal behavior.
