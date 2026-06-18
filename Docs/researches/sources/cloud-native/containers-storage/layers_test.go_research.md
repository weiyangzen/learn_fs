# sources/cloud-native/containers-storage/layers_test.go

## Purpose
This test file checks the small `layerLocations` bitmask helpers used by `layers.go` to map stable, image-store, and volatile layer metadata locations.

## Important Tests
`TestLayerLocationFromIndex` asserts exact bit values for indexes 0 through 4. `TestLayerLocationFromIndexAndToIndex` iterates over every bit in the `layerLocations` storage size and verifies `indexFromLayerLocation(layerLocationFromIndex(i)) == i`.

## Control Flow and State
The tests are pure and do not touch filesystem state. They use `unsafe.Sizeof` to cover the full bit width of the `layerLocations` type.

## Dependencies and Integration Points
The file depends on `testify/assert`, `testify/require`, and `unsafe`. These helpers are used by `layers.go` when iterating JSON path arrays and deciding which layer metadata file a layer belongs to.

## Risks and Edge Cases
The tests do not check invalid multi-bit `layerLocations` inputs to `indexFromLayerLocation`; callers should pass one-bit values. They also do not cover the semantic relationship between the first three indexes and the current `numLayerLocationIndex`.

## Test Signals
The tests provide focused confidence that the bit-shift/trailing-zero helpers remain inverses for one-bit values, which protects persistence-location indexing logic in `saveLayers` and `load`.
