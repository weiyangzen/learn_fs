# sources/cloud-native/moby/daemon/volume/service/by.go

## Purpose
Defines composable in-memory volume filters for `VolumeStore.Find`.

## Important APIs, Types, And Functions
`By` is the marker interface. Constructors/types include `ByDriver`, `ByReferenced`, `And`, `Or`, `CustomFilter`, `FromList`, and `byLabelFilter`.

## Control Flow
Filters are marker values interpreted by `VolumeStore.filter`. `byLabelFilter` returns a `CustomFilter` that requires `volume.DetailedVolume`, matches positive `label` filters, and rejects volumes matching `label!`.

## State And Persistence
No state is persisted; filters operate on volume lists and store reference state.

## Dependencies And Integration Points
Used by service list/prune/local-size flows and store tests. Integrates daemon filter args and detailed volume labels.

## Risks
Label filtering excludes volumes that do not implement `DetailedVolume`. `Or`/`And` behavior is implemented elsewhere, so new filter types require updates in `VolumeStore.filter`.

## Test Signals
Service list/prune and store filter tests cover driver, dangling/reference, label, and custom filtering behavior.
