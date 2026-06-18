<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/scope_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/scope_test.go

## Purpose
Tests Docker registry auth scope formatting and context aggregation.

## Important APIs, Types, And Functions
- `TestRepositoryScope` validates repo path extraction and pull/push scope strings.
- `TestGetTokenScopes` validates merging, sorting, and exact-string deduplication.
- `TestCustomScope` validates arbitrary scopes plus appended pull repo scopes.

## Control Flow
Tests construct `reference.Spec` values or contexts with `tokenScopesKey{}` and call the scope helpers directly.

## State And Persistence
No persistent state; all scope data is context-local.

## Dependencies And Integration Points
Protects behavior consumed by Docker authorizers during resolve, fetch, push, and cross-repo mount requests.

## Risks And Edge Cases
Tests confirm exact-string deduplication but also reveal semantic duplicates with different action ordering are not collapsed.

## Test Signals
Focused unit coverage of scope string and ordering behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/scope_test.go -->
