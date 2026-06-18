# Research: sources/cloud-native/buildkit/exporter/containerimage/exptypes/annotations.go

## Purpose
Annotation key grammar for container image exporter.

## Important APIs, Types, and Functions
Target constants, regex/parser state, `AnnotationKey`, string constructors, and `ParseAnnotationKey`.

## Control Flow
Parses metadata keys into target type, optional platform, and annotation key; constructors produce canonical keys.

## State and Persistence
Only compiled regex/global parser state.

## Dependencies and Integration Points
Depends on containerd platform parsing and OCI platforms. Shared contract for clients setting exporter annotations.

## Risks and Edge Cases
Grammar changes are compatibility-sensitive.

## Test Signals
Parser/exporter annotation tests expected.
