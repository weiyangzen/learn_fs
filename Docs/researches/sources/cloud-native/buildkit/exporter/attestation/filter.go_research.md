# Research: sources/cloud-native/buildkit/exporter/attestation/filter.go

## Purpose
Predicate-type filter for BuildKit attestations.

## Important APIs, Types, and Functions
`Filter` accepts attestations plus include/exclude predicate maps.

## Control Flow
Iterates attestations, checks predicate-type metadata, applies include/exclude rules, and preserves accepted order.

## State and Persistence
Pure slice filtering; no state.

## Dependencies and Integration Points
Depends on exporter attestation metadata layout. Used by image writer to omit inline-only or selected attestations.

## Risks and Edge Cases
Missing/unexpected predicate metadata can filter incorrectly.

## Test Signals
No direct tests in this subset.
