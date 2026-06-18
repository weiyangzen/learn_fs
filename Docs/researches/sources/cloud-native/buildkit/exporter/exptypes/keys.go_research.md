# Research: sources/cloud-native/buildkit/exporter/exptypes/keys.go

## Purpose
Shared exporter option key constants.

## Important APIs, Types, and Functions
`ExporterOptKey` plus common keys such as source date epoch and build info image config attrs.

## Control Flow
No runtime flow; constants are consumed by exporter parsers and frontend metadata plumbing.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on strings only. Stable client/frontend contract outside image-specific keys.

## Risks and Edge Cases
Changing strings is compatibility-breaking.

## Test Signals
Indirect exporter option tests.
