# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/service.go

## Purpose
This file defines the `SecretService` interface and cached/uncached factory.

## Important APIs, Types, And Functions
It defines `SecretService` and `NewSecretService`.

## Control Flow
`NewSecretService` creates a base `secretService`; manager mode wraps it in `CacheSecretService` with a time-ordered secret index.

## State And Persistence
Factory state is a client pointer and optional in-memory index. Kubernetes Secrets are not mutated here.

## Dependencies And Integration Points
It is used by `API.NewAPI` and diff generation through the interface. It depends on controller-runtime client, corev1 Secret types, and dashboard index utilities.

## Risks
As with other services, cached and uncached behavior can differ if the index is stale or incomplete.

## Test Signals
No tests are present. Factory selection is the primary unit-level signal.
