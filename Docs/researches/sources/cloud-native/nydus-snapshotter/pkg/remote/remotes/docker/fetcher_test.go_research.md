# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher_test.go

## Purpose
Tests `dockerFetcher.open` around range handling, content-length reporting, server errors, and retry behavior.

## Important APIs, Types, And Functions
`TestFetcherOpen` and `TestDockerFetcherOpen` are the main tests.

## Control Flow
`TestFetcherOpen` serves random 128-byte content and varies server behavior: no range, matching content range, last byte, EOF-sized offset, and mismatched range. `TestDockerFetcherOpen` serves configured status codes and JSON bodies to assert Docker error envelope formatting, plain status formatting, and retry counts for request timeout and too many requests.

## State And Persistence
Uses local HTTP test servers only.

## Dependencies And Integration Points
Targets `dockerFetcher`, `RegistryHost`, `dockerBase.request`, Docker `Errors`, and `request.doWithRetries`.

## Risks And Edge Cases
The tests validate critical compatibility with registries that ignore range headers, but they do not cover external descriptor URLs or multi-host fallback directly.

## Test Signals
Strong direct coverage for fetch offset semantics and error reporting, including the five-response retry cap inherited from `request.retryRequest`.
