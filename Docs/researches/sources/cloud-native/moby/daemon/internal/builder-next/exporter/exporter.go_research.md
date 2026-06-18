# sources/cloud-native/moby/daemon/internal/builder-next/exporter/exporter.go

## Purpose
Defines shared constants and metadata types for Moby-specific BuildKit exporters.

## APIs, Control Flow, and Integration
`Moby` names the custom exporter type. `BuildRefLabel` prefixes content labels that track build references. `BuildRefLabelValue` stores optional `createdAt` timestamp metadata as JSON. The wrapper and moby exporter use these symbols when labeling exported image config descriptors and dispatching callbacks.

## State, Dependencies, and Risks
The file has no control flow or persistence by itself; it defines the label schema persisted in containerd content metadata by `wrapper.go`. Main risk is label key compatibility: consumers must treat the timestamp as optional and avoid assuming label presence. Test coverage is indirect through exporter wrapper behavior.
