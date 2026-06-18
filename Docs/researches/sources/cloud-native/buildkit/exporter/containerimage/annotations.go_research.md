# Research: sources/cloud-native/buildkit/exporter/containerimage/annotations.go

## Purpose
Container image exporter annotation parser/merger.

## Important APIs, Types, and Functions
`Annotations`, `AnnotationsGroup`, `ParseAnnotations`, `Platform`, `Merge`, `merge`.

## Control Flow
Scans metadata for annotation keys, parses target/platform groups, returns annotation buckets and remaining metadata, and merges sources.

## State and Persistence
Pure map transformation.

## Dependencies and Integration Points
Depends on OCI platforms, containerd platform matching, and exptypes annotation parsing. Used before image manifest/index commit.

## Risks and Edge Cases
Wrong key parsing can place annotations on wrong descriptors or reject valid exports.

## Test Signals
Indirect exporter tests.
