# Research: sources/cloud-native/buildkit/exporter/containerimage/writer.go

## Purpose
Image writer for OCI/Docker manifests, configs, indexes, layers, inline cache, timestamps, and attestations.

## Important APIs, Types, and Functions
`WriterOpt`, `ImageWriter`, `Commit`, `exportLayers`, timestamp rewrite helpers, manifest commit helpers, config/history helpers, annotation cleanup, ref metadata helpers.

## Control Flow
Validates options, parses platforms, chooses single manifest vs index, exports layers, rewrites timestamps, patches config/history/rootfs/inline cache, writes blobs with GC labels, unbundles/supplements attestations, commits attestation manifests, and writes indexes.

## State and Persistence
Persists blobs in content store; inline cache in config JSON; attestations as separate manifests/layers. Lease lifetime is managed by the exporter.

## Dependencies and Integration Points
Depends on containerd content/diff/images labels, BuildKit cache/session/solver/exporter/attestation/epoch/compression utilities, Docker/OCI specs, in-toto, package-url, tracing/progress. Central content producer for `type=image` export.

## Risks and Edge Cases
Multi-platform mapping, media type modes, annotations, reproducible timestamps, lazy providers, attestation subjects, and layer/history normalization are high-risk.

## Test Signals
Broad image exporter integration tests.
