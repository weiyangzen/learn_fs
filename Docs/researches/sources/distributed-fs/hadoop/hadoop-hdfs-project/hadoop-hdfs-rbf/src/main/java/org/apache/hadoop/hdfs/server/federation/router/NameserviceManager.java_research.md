# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NameserviceManager.java

## Purpose
`NameserviceManager` defines the admin contract for disabling, enabling, and listing disabled nameservices in Router-Based Federation.

## Important APIs, Types, And Functions
- `disableNameservice(DisableNameserviceRequest)` returns a `DisableNameserviceResponse`.
- `enableNameservice(EnableNameserviceRequest)` returns an `EnableNameserviceResponse`.
- `getDisabledNameservices(GetDisabledNameservicesRequest)` returns a `GetDisabledNameservicesResponse`.

## Control Flow
The interface has no implementation. `RouterAdminServer` implements this contract through the protobuf admin translator. Its implementation verifies superuser privilege, validates namespace existence or disabled-state membership, and delegates to `DisabledNameserviceStore`.

## State And Persistence
The interface owns no state. Implementations persist disabled nameservice state through the federation state store's `DisabledNameserviceStore`, allowing routers to avoid routing to administratively disabled namespaces.

## Dependencies And Integration Points
It depends on state-store protocol request/response types. `RouterClient.getNameserviceManager` exposes a remote proxy for callers such as admin CLI tooling and tests.

## Risks And Edge Cases
Because this is an interface, compatibility depends on protobuf translators and implementers preserving request/response semantics. Disabling a nonexistent namespace should fail cleanly; enabling a namespace not currently disabled should also report failure. Authorization is implementation-specific and must not be bypassed by alternate implementations.

## Test Signals
`TestDisableNameservices`, `TestRouterAdmin`, and admin CLI tests exercise the implementation path through `RouterAdminServer` and `RouterClient`/translator proxies.
