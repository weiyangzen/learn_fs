# sources/control-plane/ceph-csi/internal/kms/dummy.go

## Purpose
`dummy.go` provides test-only KMS dummy provider registration utilities for code that needs an `EncryptionKMS` without contacting external systems.

## Important APIs, Types, And Functions
`TestDummyFunc` constructs an `EncryptionKMS`. `ProviderTest` describes a test provider. `kmsTestProviderList` holds registered test providers. `RegisterTestProvider()`, `GetKMSTestDummy()`, and `GetKMSTestProvider()` manage the test registry. `newDefaultTestDummy()` returns a `secretsKMS`; `newSecretsMetadataTestDummy()` returns a configured `secretsMetadataKMS`.

## Control Flow And State
Package initialization registers dummy providers for `metadata` and `default`. Lookups return nil when no matching dummy provider exists. The metadata dummy sets a test passphrase, tenant, and nil config.

## State And Persistence Behavior
The registry is a process-global map. Dummy KMS objects keep passphrases in memory and do not talk to Kubernetes or external KMS providers.

## Dependencies And Integration Points
The file depends on base64 encoding and the main KMS interfaces/types. It supports tests in other packages that need provider-shaped KMS values.

## Risks And Edge Cases
`RegisterTestProvider()` does not validate empty IDs, duplicate IDs, or nil constructors, unlike production `RegisterProvider()`. The global mutable map is not protected by a mutex. The dummy passphrases are hardcoded and unsuitable for production.

## Test Signals
No direct tests are in this subset. Indirect coverage occurs when other tests call the dummy registry. Useful coverage would assert missing lookup, duplicate behavior, and dummy encryption/decryption compatibility.
