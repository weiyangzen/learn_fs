## sources/cloud-native/moby/daemon/internal/layer/layer_unix_test.go

Purpose: Tests layer size accounting on non-Windows builds.

Important helper/test: `graphDiffSize` extracts the underlying `roLayer` and calls graphdriver `DiffSize`. `TestLayerSize` creates two layers with known file contents and verifies both graphdriver diff sizes and layer cumulative sizes.

Control flow and state: Uses `newTestStore` and `createLayer` from `layer_test.go`, then compares expected byte lengths for base and child layers.

Dependencies and integration: Exercises graphdriver `DiffSize` and `Layer.Size` on Unix-like platforms. The build tag excludes Windows because its graphdriver does not support the same Changes/DiffSize path.

Risks covered: Cumulative size calculation and per-layer diff size. Gaps include sparse files, whiteouts, metadata-only changes, and compression effects.

Persistence: Temporary graphdriver/layerdb state.
