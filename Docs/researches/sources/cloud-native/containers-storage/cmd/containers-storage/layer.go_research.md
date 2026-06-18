<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/layer.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/layer.go

- Purpose: Implements per-layer inspection, big-data operations, and parent-owner reporting.
- Important functions: `listLayerBigData`, `getLayerBigData`, `setLayerBigData`, `layer`, and `layerParentOwners`.
- Control flow: Resolve layer ID/name, display metadata, list/read/write big-data items, or traverse parent owners.
- State and persistence: `setLayerBigData` writes persistent layer big-data files; other commands are read-only.
- Dependencies and integration: Uses storage layer APIs and command flags.
- Risks: Big-data mutation can change layer metadata assumptions; parent ownership output depends on consistent layer graph.
- Test signals: CLI layer creation/data tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/layer.go -->
