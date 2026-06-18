# sources/cloud-native/moby/daemon/internal/builder-next/worker/worker_test.go

## Purpose
Tests platform list merging for the Moby BuildKit worker.

## APIs, Control Flow, and Integration
`TestMergePlatforms` defines default, Windows, and Darwin/arm64 platforms and covers unique, overlapping, empty-supported, empty-defined, and both-empty cases. It asserts result length and that expected platforms are present using `gotest.tools`.

## State, Dependencies, and Risks
No external state. The test confirms `mergePlatforms` deduplicates using platform matchers while preserving desired membership. It does not assert order or the mutating behavior of `Worker.Platforms(noCache)`, and it does not cover source registration, executor, export, remote import, or cache operations.
