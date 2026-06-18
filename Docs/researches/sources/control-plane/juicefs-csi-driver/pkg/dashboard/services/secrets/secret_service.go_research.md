# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/secret_service.go

## Purpose
This is the uncached secret service for listing JuiceFS-related Kubernetes Secrets.

## Important APIs, Types, And Functions
It defines `secretService` and `ListAllSecrets`.

## Control Flow
`ListAllSecrets` lists all Secrets visible to the client, filters to generated JuiceFS secrets or custom JuiceFS credential secrets using dashboard utility predicates, and returns the filtered slice.

## State And Persistence
The service is stateless and read-only.

## Dependencies And Integration Points
It depends on controller-runtime client, corev1 Secrets, and `utils.IsJuiceSecret`/`IsJuiceCustSecret`. It feeds diff generation in `batch.go`.

## Risks
Listing all secrets can be expensive and may require broad RBAC. The local variable `seccretList` is misspelled but harmless. Filtering by `token`/`metaurl` fields can include user secrets not intended for dashboard diffing if RBAC permits them.

## Test Signals
No tests are present. Tests should verify both generated-label and custom-secret filters.
