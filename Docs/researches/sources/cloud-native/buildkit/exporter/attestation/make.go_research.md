# Research: sources/cloud-native/buildkit/exporter/attestation/make.go

## Purpose
Creates in-toto statements from BuildKit attestation results.

## Important APIs, Types, and Functions
`ReadAll`, `MakeInTotoStatements`, and `makeInTotoStatement`.

## Control Flow
Reads attestation content from refs/remotes or inline data, parses/wraps JSON, normalizes predicate type and subjects, and returns statements concurrently.

## State and Persistence
No persistence; reads session/snapshot content and returns memory objects.

## Dependencies and Integration Points
Depends on in-toto, exporter/result/session/snapshot APIs, gateway metadata, errgroup. Used by image writer before committing attestation manifests.

## Risks and Edge Cases
Statement format/subject defaults and concurrent ordering/error propagation are correctness-sensitive.

## Test Signals
Covered by provenance/SBOM export integration tests.
