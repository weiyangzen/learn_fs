# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/scope.go

## Purpose
Builds and carries Docker registry authorization scopes through contexts so token requests receive the required repository permissions.

## Important APIs, Types, And Functions
`RepositoryScope`, `ContextWithRepositoryScope`, `WithScope`, `ContextWithAppendPullRepositoryScope`, and `GetTokenScopes`.

## Control Flow
`RepositoryScope` parses the reference locator and emits `repository:<repo>:pull` or `repository:<repo>:pull,push`. Context helpers append scopes under a private key. `GetTokenScopes` merges context scopes with challenge-provided common scopes, sorts them, and removes exact duplicates.

## State And Persistence
Scopes live only in derived contexts. No global or persistent state.

## Dependencies And Integration Points
Used by fetcher, resolver, pusher, referrers, and authorizer token generation. Pull/push and mount-from flows rely on correct scope composition.

## Risks And Edge Cases
Deduplication is exact string-based and does not normalize semantically equivalent scope actions such as `pull,push` versus `push,pull`. The context value is type-asserted to `[]string`, so only package helpers should set it.

## Test Signals
`scope_test.go` covers pull/push scope generation, duplicate removal, sorting, and custom scope composition.
