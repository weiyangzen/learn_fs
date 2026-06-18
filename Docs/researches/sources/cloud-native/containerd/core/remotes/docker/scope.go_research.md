<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/scope.go -->
# sources/cloud-native/containerd/core/remotes/docker/scope.go

## Purpose
Builds and stores Docker registry auth scopes in context for pull, push, and cross-repository mount flows.

## Important APIs, Types, And Functions
- `RepositoryScope(refspec, push)` formats `repository:<repo>:pull` or `repository:<repo>:pull,push`.
- `ContextWithRepositoryScope(ctx, refspec, push)` appends the repository scope to context.
- `WithScope(ctx, scope)` appends arbitrary scope strings under a private context key.
- `ContextWithAppendPullRepositoryScope(ctx, repo)` appends a pull scope for an additional repo, used for mount sources.
- `GetTokenScopes(ctx, common)` returns sorted, deduplicated context and common scopes.

## Control Flow
References are parsed as dummy URLs to derive the repository path from the locator. Scopes are accumulated in a context value slice and then merged with common scopes. Deduplication happens after lexicographic sorting and is string-exact.

## State And Persistence
Scopes live only in `context.Context`. No global or persistent state is used.

## Dependencies And Integration Points
Used by resolver/fetcher/pusher before making registry requests so authorizers can request tokens with proper scopes. Cross-repo mount uses appended pull scope for the source repo.

## Risks And Edge Cases
Deduplication is syntax-based, not semantic; `pull,push` and `push,pull` are distinct. `WithScope` assumes any existing context value has the expected `[]string` type.

## Test Signals
`scope_test.go` covers pull vs pull/push scope formatting, sorted/deduplicated merging, and custom scope accumulation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/scope.go -->
