# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/scope_test.go

## Purpose
Tests Docker registry scope generation and scope aggregation from contexts.

## Important APIs, Types, And Functions
`TestRepositoryScope`, `TestGetTokenScopes`, and `TestCustomScope`.

## Control Flow
The tests create reference specs with and without ports, assert pull and pull/push repository scopes, then verify `GetTokenScopes` output for empty, common-only, context-only, duplicate, and mixed scope lists. Custom scope testing combines arbitrary scope with appended repository pull scope.

## State And Persistence
No state beyond context values.

## Dependencies And Integration Points
These tests protect the scopes consumed by `dockerAuthorizer.doBearerAuth` and registry token endpoints.

## Risks And Edge Cases
The tests document exact string ordering and dedupe semantics, including the lack of grammar-aware action normalization.

## Test Signals
Direct unit coverage for auth scope behavior across pull, push, and custom mount-related scope additions.
