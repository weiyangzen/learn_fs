# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/volumes.go

## Purpose
`volumes.go` builds Kubernetes projected volumes and volume mounts for KMS-related secret material needed by OSD prepare/daemon pods. It maps Vault TLS/token Secrets into `/etc/vault` and KMIP certificate/key material into the KMIP config directory.

## Important APIs, Types, and Functions
`VaultSecretVolumeAndMount()` returns the list of `VolumeProjection` entries for Vault TLS and token Secrets. `VaultVolumeAndMount()` and `VaultVolumeAndMountWithCustomName()` wrap those projections in a named `Volume` and `VolumeMount`. `tlsSecretPath()` maps Vault TLS env options to filenames (`vault.ca`, `vault.crt`, `vault.key`). `KMIPVolumeAndMount()` creates a projected volume containing `ca.crt`, `client.crt`, and `client.key`.

## Control Flow
Vault projection generation iterates over `cephv1.VaultTLSConnectionDetails`, checks each configured value with `GetParam()`, and adds a Secret projection with mode `0444`, the expected Secret key from `tlsSecretKeyToCheck()`, and a fixed path from `tlsSecretPath()`. If a token Secret name is provided, it appends a projection of key `token` to `vault.token`. The custom-name variant skips volume creation only when both config map and token name are empty; otherwise it names the volume `vault` plus suffix and mounts it at `/etc/vault` or `/etc/vault/<custom>`.

## State and Persistence
The functions only construct Kubernetes pod specs; persistence is in Kubernetes Secrets mounted as projected volumes. Secret file mode is intentionally world-readable (`0444`) because containers run as the `rook` user while Secrets are mounted as root. The mounts are read-only.

## Dependencies and Integration Points
The file depends on Kubernetes corev1 API types, Vault API option names, `libopenstorage/secrets` provider constants, KMIP constants from sibling files, and `vault.go` key mapping. Operator code can use these helpers when assembling deployments/jobs that need Vault or KMIP credentials.

## Risks
The `len(kmsVaultConfigFiles) == 0` check means a non-empty map with no KMS-related entries still creates an empty projected Vault volume; this is intentionally covered by tests but can surprise callers. `KMIPVolumeAndMount()` assumes the token Secret contains all three required keys and does not support optional entries. Mode `0444` trades stricter permissions for non-root readability.

## Test Signals
`volumes_test.go` covers TLS path mapping, Vault projection combinations for CA/client cert/client key/token, custom volume names and mount paths, empty/non-KMS maps, and KMIP volume projection shape. These tests are structural and do not validate pod admission or Secret existence.
