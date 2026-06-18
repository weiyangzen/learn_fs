# Research: sources/cloud-native/buildkit/exporter/containerimage/exptypes/keys.go

## Purpose
Container image exporter option key constants.

## Important APIs, Types, and Functions
`ImageExporterOptKey` and keys for names, push, OCI media types, compression, annotations, unpack/store, timestamps, attestations, and response metadata.

## Control Flow
No runtime flow; constants are consumed by parsers and clients.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends only on string constants. String contract between BuildKit clients/frontends and image exporter.

## Risks and Edge Cases
Renaming keys is compatibility-breaking.

## Test Signals
Coverage is indirect through option parsing tests.
