# Research: sources/cloud-native/buildkit/exporter/containerimage/opts.go

## Purpose
Image commit option parser/validator.

## Important APIs, Types, and Functions
`ImageCommitOpts`, `Load`, `Validate`, `SetOCITypesDefault`, `OCITypesEnabled`, bool/map helpers.

## Control Flow
Parses exporter option strings into compression/ref config, names, OCI media behavior, annotations, epoch/rewrite, attestation flags, and returns unconsumed metadata.

## State and Persistence
Per-export struct only.

## Dependencies and Integration Points
Depends on cache config, compression, epoch parsing, exptypes keys. Used by `Resolve` and `ImageWriter.Commit`.

## Risks and Edge Cases
Option compatibility and clear validation errors are critical.

## Test Signals
Exporter integration tests.
