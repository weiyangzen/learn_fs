# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/volumes_test.go

## Purpose
`volumes_test.go` verifies that the KMS volume helpers emit exact Kubernetes `VolumeProjection`, `Volume`, and `VolumeMount` structures. It is a spec-shape test suite for Vault and KMIP credential mounts.

## Important APIs, Types, and Functions
`Test_tlsSecretPath()` covers Vault TLS option to mounted filename mapping. `TestVaultSecretVolumeAndMount()` checks projection lists for empty input, CA only, CA plus client cert, CA plus client cert/key, token only, and mixed token/TLS cases. `TestVaultVolumeAndMountWithCustomName()` checks full volume/mount outputs with and without custom suffixes. `TestKMIPVolumeAndMount()` checks KMIP projected Secret items and mount path.

## Control Flow
The tests build expected Kubernetes API objects with mode `0444` and compare returned objects with `reflect.DeepEqual`. Vault projections are expected in the same order as `cephv1.VaultTLSConnectionDetails`, followed by the token projection. Custom Vault names append the suffix to both volume name and `/etc/vault/<suffix>` mount path.

## State and Persistence
There is no external state. The tests construct in-memory Kubernetes API objects only. They encode the persistence contract indirectly: credential data must be supplied by Kubernetes Secrets with keys `cert`, `key`, or `token`, and pods will see files named `vault.ca`, `vault.crt`, `vault.key`, or `vault.token`.

## Dependencies and Integration Points
The suite depends on corev1 Kubernetes types, `libopenstorage/secrets.TypeVault`, Vault env option strings through literals, and KMIP constants. It cross-checks assumptions shared with `vault.go` validation and TLS temp-file conversion.

## Risks
Exact deep equality makes the suite sensitive to harmless Kubernetes struct defaulting differences if helpers start setting optional fields. The tests do not verify invalid/missing Secret names because these helpers are pure pod-spec builders; validation is handled elsewhere. They also do not exercise pod security context interactions with `0444` file mode.

## Test Signals
Good signals are the exhaustive Vault projection combinations and custom mount path checks. Additional signals would include a case for all three KMIP keys with an empty token Secret name if callers might pass empty names.
