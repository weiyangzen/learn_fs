# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher_fuzz.go

## Purpose
Provides fuzz entry points for fetcher HTTP read behavior and Docker reference parsing.

## Important APIs, Types, And Functions
`FuzzFetcher(data []byte) int` builds an HTTP test server and reads through `dockerFetcher.open`. `FuzzParseDockerRef(data []byte) int` calls distribution reference parsing.

## Control Flow
For non-empty data, the fuzzer serves the bytes with content range/length headers, constructs a local registry host, opens offset zero, reads all bytes, and panics if length differs from input. The reference fuzzer simply parses arbitrary input and ignores errors.

## State And Persistence
Uses an ephemeral `httptest.Server`; no persistent state.

## Dependencies And Integration Points
Compiled under `gofuzz`. Exercises `dockerBase.request`, fetcher open logic, and distribution reference parsing.

## Risks And Edge Cases
Only offset zero is fuzzed, so it does not explore the discard/seek code paths. It checks length but not byte equality.

## Test Signals
Complements `fetcher_test.go` by expanding input bytes and server content sizes for panic detection.
