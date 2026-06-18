# sources/cloud-native/buildkit/cache/opts.go

## Purpose

`opts.go` defines lightweight option and descriptor-handler types that flow through cache ref creation, lookup, lazy remote-provider validation, and unlazy operations. It is the small glue layer between cache refs, session groups, content providers, and progress reporting.

## Important APIs, Types, and Functions

- `DescHandler` describes how to access a remote/lazy descriptor: a session-aware `content.Provider`, progress controller, snapshot labels, annotations, and a `Ref` string for sync/progress identity.
- `DescHandlers` maps blob digests to descriptor handlers and is passed as a `RefOption`.
- `descHandlersOf` extracts the first `DescHandlers` option from variadic ref options.
- `DescHandlerKey` aliases digest but is not used in this file.
- `NeedsRemoteProviderError` is a slice of missing digests and reports missing descriptor handlers for lazy blobs.
- `Unlazy` aliases `session.Group`, and `unlazySessionOf` extracts a session group from ref options.

## Control Flow

Cache manager methods accept variadic `RefOption` values. `descHandlersOf` scans those options when loading or creating refs so lazy blob records can be checked against available remote providers. `unlazySessionOf` is used by `GetByBlob` to optionally force unlazy of a newly created blob ref using a session group passed as an option.

## State and Persistence Behavior

This file defines no persistent state. `DescHandlers` are in-memory capabilities attached to returned refs so later `Extract`, `Mount`, `GetRemotes`, or content reads can materialize lazy content. `NeedsRemoteProviderError` carries transient missing-provider state to callers.

## Dependencies and Integration Points

The option types integrate containerd `content.Provider`, BuildKit `session.Group`, BuildKit progress, and OCI digests. They are consumed by `manager.go`, `refs.go`, and `remote.go` whenever lazy content may require a provider or snapshotter labels.

## Risks and Edge Cases

- `descHandlersOf` returns only the first `DescHandlers` instance; multiple maps are not merged.
- `unlazySessionOf` checks for `session.Group`, while the declared `Unlazy` alias is not directly matched unless values also satisfy `session.Group`.
- A nil or incomplete `DescHandler` can allow metadata creation but later fail during unlazy if a provider is required.

## Test Signals

`manager_test.go` uses `DescHandlers` extensively for lazy blob imports, extraction, compression conversion, and remote descriptor generation. Missing handler behavior is exercised indirectly through lazy access failures.
