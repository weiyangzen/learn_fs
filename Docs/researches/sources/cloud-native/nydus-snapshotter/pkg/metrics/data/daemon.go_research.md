# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/daemon.go

This file declares daemon-level Prometheus metrics. `NydusdEventCount` counts lifetime events by daemon state/event label. `NydusdCount` tracks daemon count by nydusd version. `NydusdRSS` is a TTL-backed gauge for daemon memory RSS by daemon ID. `NydusdImageInfo` maps daemon IDs to served image references.

The metrics are registered by `metrics/registry` and updated by collectors in `metrics/collector/daemon.go`, liveness monitor, manager start/recovery/destroy paths, and daemon RAFS add/remove methods. State is metric state only; there are no files or external resources.

Risks include balancing count increments/decrements across recovery, hot upgrade, and destroy paths; daemon ID and image ref label cardinality; and stale RSS label cleanup depending on TTL. `NydusdImageInfo` is not TTL-backed and relies on explicit deletion when RAFS instances are removed. There are no direct tests for these metric definitions.
