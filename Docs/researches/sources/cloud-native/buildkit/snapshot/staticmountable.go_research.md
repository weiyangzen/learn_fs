## sources/cloud-native/buildkit/snapshot/staticmountable.go

Purpose: implements a simple immutable `Mountable` backed by a static mount slice and optional identity mapping.

Important APIs/types/functions: `staticMountable.Mount` returns a copy of mounts, applies redirect_dir option if needed, increments an atomic count, and returns a release function that decrements the count. `IdentityMapping` returns the stored idmap.

Control flow: mount calls do not perform OS mounts; they hand out mount metadata and release bookkeeping. If release count goes below zero and `BUILDKIT_DEBUG_PANIC_ON_ERROR=1`, the release function panics.

State and persistence: in-memory atomic count tracks outstanding mount references. No persistence.

Dependencies and integration points: used by `FromContainerdSnapshotter.Mounts` and `View`. Redirect_dir option shares logic with snapshotter adapter.

Risks and test signals: double release normally only decrements below zero silently unless debug panic is enabled. Returning a shallow copy of mount structs protects slice structure but options slices are still shared by value unless replaced by redirect_dir logic.
