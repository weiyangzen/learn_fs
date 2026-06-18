# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/security.go

Purpose: provides helper predicates for `KeyManagementServiceSpec`, especially Vault, Azure, IBM Key Protect, KMIP, token, Kubernetes, agent, and TLS configuration detection.

Important APIs/types/functions: `VaultTLSConnectionDetails`, `KeyManagementServiceSpec.IsEnabled`, `IsTokenAuthEnabled`, `IsK8sAuthEnabled`, `IsAgentAuthEnabled`, `IsVaultKMS`, `IsAzureMS`, `IsIBMKeyProtectKMS`, `IsKMIPKMS`, `IsTLSEnabled`, and `getParam`.

Control flow: `IsEnabled` checks whether any connection details exist. Token auth is enabled by a non-empty token secret name. Kubernetes auth is enabled when `VAULT_AUTH_METHOD` equals the Vault library's Kubernetes value and no token secret is configured. Agent auth is enabled when that auth method equals `"agent"` and no token secret is configured. Provider helpers inspect `KMS_PROVIDER` against provider constants or literal provider names. TLS detection scans the Vault CA cert, client cert, and client key environment option names and returns true on the first non-empty configured value. `getParam` trims whitespace from non-empty map values.

State and persistence: no persistence or mutation. Helpers read the CRD's `ConnectionDetails` map and token field.

Dependencies/integration: depends on HashiCorp Vault API env-var constants, libopenstorage secrets provider constants, and Vault auth-method constants. Ceph encryption and KMS integration code uses these predicates to select authentication and provider setup paths.

Risks: methods are not nil-receiver safe. `IsEnabled` treats a map with only empty values as enabled because it checks length only. `getParam` checks emptiness before trimming, so a whitespace-only value is considered present by the `ok && val != ""` guard but returns empty after trim. Provider names are case-sensitive.

Test signals: `security_test.go` covers agent and Kubernetes auth interactions with token secret presence and auth-method values. Provider, TLS, token, enabled, and trimming behavior are not directly covered here.
