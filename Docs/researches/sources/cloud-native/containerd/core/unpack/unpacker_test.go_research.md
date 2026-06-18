# sources/cloud-native/containerd/core/unpack/unpacker_test.go

## Purpose
This file benchmarks chain ID calculation strategies and tests overlay mount conversion used by parallel overlayfs unpack.

## Important APIs, Types, and Functions
`generateRandomDiffIDs` creates benchmark inputs. `BenchmarkUnpackWithChainID` simulates repeated `identity.ChainID` calculation. `BenchmarkUnpackWithChainIDs` benchmarks precomputed `identity.ChainIDs`. `TestBindToOverlay` validates `bindToOverlay`.

## Control Flow
Benchmarks run for 5, 10, 25, and 50 layers. The unit test checks single bind mount conversion, overlay passthrough, and multiple-mount passthrough.

## State and Persistence
No persistence; all data is generated in memory.

## Dependencies and Integration Points
Uses `go-digest`, OCI identity helpers, and `core/mount`. The test protects an unpacker workaround needed when parallel overlayfs snapshotters provide bind mounts.

## Risks
Benchmarks are performance signals only and do not enforce thresholds. `bindToOverlay` test does not cover all mount option permutations.

## Test Signals
Confirms precomputed chain IDs are the intended optimization path and that only a single bind mount is rewritten to overlay with `upperdir` and no `rbind`.
