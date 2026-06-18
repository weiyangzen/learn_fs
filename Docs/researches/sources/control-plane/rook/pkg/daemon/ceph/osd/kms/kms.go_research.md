# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kms.go

## Purpose
`kms.go` is the generic KMS dispatch layer for encrypted Ceph OSD keys. It normalizes the configured provider, validates KMS connection details, and routes put/get/update/delete operations to Kubernetes Secrets, Vault, IBM Key Protect, KMIP, or Azure Key Vault. It is the common API used by OSD encryption workflows so the rest of the OSD code can work through one `Config` object rather than directly binding to each backend.

## Important APIs, Types, and Functions
The central type is `Config`, which stores the selected `Provider`, the cluster daemon context, the `CephCluster` spec, and `ClusterInfo`. `NewConfig()` chooses the provider from `clusterSpec.Security.KeyManagementService.ConnectionDetails[KMS_PROVIDER]`, defaulting to Kubernetes when the provider is empty and logging unsupported values. `PutSecret()`, `GetSecret()`, `UpdateSecret()`, and `DeleteSecret()` are the public backend operations. `ValidateConnectionDetails()` enforces mandatory provider fields and loads token-secret data into connection details or process environment. `SetTokenToEnvVar()` is a narrower helper for Vault token injection. `GetParam()` trims whitespace and treats missing or empty entries uniformly. The private `putSecret()`, `getSecret()`, and `deleteSecret()` helpers adapt `libopenstorage/secrets.Secrets`.

## Control Flow
Provider selection is mostly branch based. Kubernetes stores the raw secret in Kubernetes Secret helpers from sibling files. Vault and Azure initialize a `secrets.Secrets` implementation, transform OSD key names with `GenerateOSDEncryptionSecretName()`, and operate with provider-specific key context. IBM creates imported keys with aliases and treats `KEY_ALIAS_NOT_UNIQUE_ERR` as idempotent success. KMIP registers the key with the KMIP server but persists the returned unique identifier in a Kubernetes Secret; later reads and deletes use that identifier to access KMIP. Validation first checks `KMS_PROVIDER`, then token-auth requirements, then provider-specific mandatory fields. Vault `kv` backends get an auto-detected backend version when `VAULT_BACKEND` is absent.

## State and Persistence
State persists in the configured external KMS and, for Kubernetes and KMIP, in Kubernetes Secrets. Vault and Azure secret names are transformed into Rook OSD encryption secret names; KMIP stores only the KMIP unique identifier in Kubernetes, not the encryption key. Vault namespace and KV-v2 destroy behavior are encoded in the key-context map. `ValidateConnectionDetails()` mutates `kms.ConnectionDetails` for IBM/KMIP token content and sets `VAULT_TOKEN` in the process environment for Vault token auth.

## Dependencies and Integration Points
The file integrates with `libopenstorage/secrets`, HashiCorp Vault API constants, IBM Key Protect client types, Kubernetes API errors, Rook `ClusterSpec`, and OSD encryption naming helpers. It calls provider initializers from sibling KMS files: Vault, IBM, KMIP, Azure, and Kubernetes helpers. It is used by OSD prepare/activation and key-rotation paths that need a uniform encrypted-key lifecycle.

## Risks
Provider operations are not an exclusive `switch` in several methods; they rely on mutually exclusive `Is*` checks. Unsupported provider values are logged in `NewConfig()` but leave `Provider` empty, so later operations may silently no-op or return generic unsupported errors depending on method. `getSecret()` assumes `s[secretName]` is a string and can panic if the secrets backend returns an unexpected shape. Vault token validation writes to global process environment, which can leak across tests or concurrent code. IBM delete uses `context.TODO()` because cluster deletion cancels the cluster context; this is intentional but can outlive caller cancellation.

## Test Signals
`kms_test.go` exercises validation for missing provider, Vault token and TLS secrets, IBM token/instance fields, KMIP token material, Azure mandatory fields, and Vault token env injection. It does not deeply mock `PutSecret()`/`GetSecret()`/`DeleteSecret()` backend calls for every provider, so regressions in provider client behavior or `getSecret()` type assertions require integration or provider-specific tests.
