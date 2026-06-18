# Research: sources/cloud-native/nydus-snapshotter/pkg/prefetch/prefetch.go

This file implements a global in-memory prefetch map populated by an external NRI plugin or caller. `prefetchInfo` contains a map from image reference to prefetch file list and a mutex. `Pm` is the package-level singleton.

`SetPrefetchFiles` unmarshals a JSON array of maps, initializes the map if needed, stores each `image` to `prefetch` value, and logs the full map. `GetPrefetchInfo` returns the value for an image or an empty string. `DeleteFromPrefetchMap` removes an image. `manager.BuildDaemonCommand` consumes this map for dedicated daemon startup and deletes entries after adding `--prefetch-files`.

State is process-local and not persisted, so restart loses pending prefetch hints. Dependencies are JSON and logging. Risks include accepting arbitrary map keys without schema validation, logging potentially large or sensitive prefetch data, deleting from a nil map being safe but masking missing initialization, and the global singleton making tests/order dependence likely. There are no direct tests in this subset.
