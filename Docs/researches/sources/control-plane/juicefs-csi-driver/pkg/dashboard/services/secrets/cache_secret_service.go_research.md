# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/cache_secret_service.go

## Purpose
`CacheSecretService` maintains a cached index of JuiceFS-related Secrets for dashboard diff generation.

## Important APIs, Types, And Functions
It defines `CacheSecretService`, `ListAllSecrets`, `Reconcile`, and `SetupWithManager`.

## Control Flow
`ListAllSecrets` iterates the secret index and fetches each secret. `Reconcile` fetches a secret, removes missing entries, ignores deleting objects, and indexes secrets that are either CSI-generated JuiceFS secrets or custom secrets containing token/metaurl fields. Setup watches all secret create/update/delete events and removes relevant secrets from the index on delete.

## State And Persistence
State is the in-memory `TimeOrderedIndexes[Secret]`. Secret data persists in Kubernetes and is only read by this service.

## Dependencies And Integration Points
It wraps `secretService`, uses dashboard secret classifiers in `utils/index.go`, controller-runtime manager watches, and feeds `batch.go` diff generation.

## Risks
Create/update predicates enqueue every Secret, which may be noisy in large clusters. A secret that stops matching JuiceFS criteria on update is not explicitly removed unless not-found/delete occurs, because `Reconcile` only adds matching secrets and otherwise leaves prior index entries.

## Test Signals
No direct tests are present. Tests should cover add/delete and update-from-matching-to-nonmatching behavior.
