# sources/control-plane/ceph-csi/internal/kms/azure_vault.go

## Purpose
`azure_vault.go` registers the `azure-kv` KMS provider, which stores passphrases directly as Azure Key Vault secrets.

## Important APIs, Types, And Functions
`azureKMS` stores namespace, secret name, integrated DEK behavior, vault URL, client ID, tenant ID, and client certificate. `initAzureKeyVaultKMS()` parses config and Kubernetes Secret data. `FetchDEK()`, `StoreDEK()`, and `RemoveDEK()` call Azure Key Vault secret get, set, and delete APIs. `getService()` builds a certificate credential and Key Vault client.

## Control Flow And State
Initialization resolves a default or configured Kubernetes Secret name, requires vault URL, client ID, and tenant ID, then reads a client certificate from the Secret. Each DEK operation creates a fresh Azure credential and `azsecrets.Client` before calling the service.

## State And Persistence Behavior
The DEK/passphrase is persisted in Azure Key Vault under the supplied key. `integratedDEK` means no external metadata DEK store is required. Provider state keeps connection material in memory; `Destroy()` is no-op.

## Dependencies And Integration Points
The provider uses Azure SDK `azidentity` and `azsecrets`, plus Ceph-CSI Kubernetes Secret helpers. It is instantiated through the global KMS provider registry.

## Risks And Edge Cases
The certificate parser expects the Secret to contain certificate and private key material in a format accepted by Azure SDK. Each operation rebuilds the client. Delete behavior does not purge or wait for completion. Strict unknown-key rejection can reject shared Kubernetes Secrets. Error messages contain a repeated spelling typo in "secret" but still wrap failures.

## Test Signals
`azure_vault_test.go` only checks provider registration. Runtime paths around certificate parsing, Key Vault get/set/delete, config validation, and unknown Secret keys are not covered in this subset.
