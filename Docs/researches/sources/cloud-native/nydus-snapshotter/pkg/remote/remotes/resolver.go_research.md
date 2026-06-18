# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/resolver.go

## Purpose
Defines the core resolver/fetcher/pusher interfaces used by this repository's remote content layer.

## Important APIs, Types, And Functions
Interfaces: `Resolver`, `Fetcher`, `FetcherByDigest`, `ReferrersFetcher`, and `Pusher`. Function adapters: `FetcherFunc` and `PusherFunc`.

## Control Flow
The file contains interface contracts only. A resolver maps a reference to a descriptor and creates namespace-bound fetchers/pushers. Fetchers retrieve content by descriptor, optional digest-only fetchers retrieve with incomplete descriptors, referrers fetchers return artifact referrer indexes, and pushers return content writers.

## State And Persistence
No state. Implementations decide whether content is local, remote, streamed, or persisted.

## Dependencies And Integration Points
Implemented by `dockerResolver`, `dockerFetcher`, and `dockerPusher`. Consumed by generic handlers in `handlers.go`, schema1 converter, and higher-level snapshotter pull/push logic.

## Risks And Edge Cases
The interfaces intentionally leave retry, auth, descriptor completeness, and persistence behavior to implementations. Callers must inspect optional interfaces with type assertions.

## Test Signals
`resolver_test.go` checks that Docker fetchers implement and correctly satisfy `FetcherByDigest`.
