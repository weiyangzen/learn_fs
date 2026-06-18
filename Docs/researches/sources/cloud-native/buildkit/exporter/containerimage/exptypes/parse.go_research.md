# Research: sources/cloud-native/buildkit/exporter/containerimage/exptypes/parse.go

## Purpose
Image exporter metadata parser.

## Important APIs, Types, and Functions
`ParsePlatforms` and `ParseKey`.

## Control Flow
Decodes platform metadata JSON and fetches global or platform-scoped metadata values.

## State and Persistence
Pure metadata transformation.

## Dependencies and Integration Points
Depends on JSON, containerd platform normalization, OCI platforms. Critical for multi-platform ref mapping in image export.

## Risks and Edge Cases
Bad/missing platform metadata causes multi-ref export failures.

## Test Signals
Covered indirectly by multi-platform exporter tests.
