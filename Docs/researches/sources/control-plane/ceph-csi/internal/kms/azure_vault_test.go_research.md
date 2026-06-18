# sources/control-plane/ceph-csi/internal/kms/azure_vault_test.go

## Purpose
`azure_vault_test.go` is a smoke test for Azure Key Vault KMS provider registration.

## Important APIs, Types, And Functions
`TestAzureKMSRegistered` verifies that `kmsTypeAzure` exists in `kmsManager.providers`.

## Control Flow And Test Behavior
The test runs in parallel and performs a single `require.True` assertion.

## Dependencies And Integration Points
It relies on package initialization executing the `RegisterProvider` call in `azure_vault.go`.

## Risks And Edge Cases
No provider initialization or Azure SDK behavior is tested. Registration can pass while all credential, Secret, or service interactions fail.

## Test Signals
The test proves only static provider wiring.
