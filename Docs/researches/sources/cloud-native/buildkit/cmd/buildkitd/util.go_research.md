# Research: sources/cloud-native/buildkit/cmd/buildkitd/util.go

Purpose: provides daemon utility helpers for GC flag formatting/parsing and provenance environment loading.

Important APIs and flow: `gcConfigToString` converts `GCConfig` thresholds to legacy comma-separated MB flag text by evaluating disk percentages against current disk stats. `int64ToString` formats integer slices. `stringToGCConfig` parses `Reserved[,Free[,Maximum]]` MB values into `config.DiskSpace` byte fields. `loadProvenanceEnv` reads `.json` files from a configured or default provenance directory, unmarshals each into a shared map, and returns nil when the directory is absent.

State and dependencies: reads provenance JSON from disk and disk stats for formatting; no writes. Depends on appdefaults, config types, disk stats, JSON, filesystem traversal, and error wrapping.

Risks and test signals: provenance JSON files merge into one map, so later files can overwrite earlier keys depending on directory order. GC string parsing accepts only integer MB values. There are no direct tests in this subset.
