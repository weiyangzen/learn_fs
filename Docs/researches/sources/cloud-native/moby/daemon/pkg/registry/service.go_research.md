# sources/cloud-native/moby/daemon/pkg/registry/service.go

## Purpose
Defines the daemon registry `Service`, which stores registry configuration and provides auth resolution, login/auth checks, endpoint lookup, and insecure-registry queries.

## Important APIs, Types, And Functions
`Service` holds a `serviceConfig` under an RW mutex. Public APIs include `NewService`, `ServiceConfig`, `ReplaceConfig`, `Auth`, `ResolveAuthConfig`, `LookupPullEndpoints`, `LookupPushEndpoints`, and `IsInsecureRegistry`. `APIEndpoint` describes a registry URL, TLS config, and mirror flag.

## Control Flow
Construction validates options into `serviceConfig`. `ReplaceConfig` prepares a commit closure so daemon reload can validate first and swap config later. `Auth` normalizes server address, looks up V2 endpoints without mirrors, attempts `loginV2` in order, and stops on context cancellation, deadline, or unauthorized errors. Endpoint lookup functions delegate to `lookupV2Endpoints` under lock.

## State And Persistence
Registry configuration is in-memory and atomically replaced by `ReplaceConfig` commit closures. `ServiceConfig` returns a copy to avoid external mutation.

## Dependencies And Integration Points
Integrates with daemon reload (`reloadRegistryConfig`), image pull/push resolution, registry login, auth config resolution, and distribution reference parsing.

## Risks And Edge Cases
Credentials are deliberately not sent to mirrors during `Auth`. `LookupPullEndpoints` and `LookupPushEndpoints` use `context.TODO`, so caller cancellation is not propagated there. `ReplaceConfig` separates validation from mutation, which is important for transactional daemon reload.

## Test Signals
Registry tests cover mirror inclusion/exclusion, insecure registry behavior, and reload tests verify registry mirrors/insecure registries update transactionally.
