# sources/distributed-fs/ceph/src/rgw/rgw_dencoder.cc

## Purpose
Registers RGW encode/decode test instances for selected types used by Ceph's dencoder tooling.

## Important APIs, types, and functions
`obj_version::generate_test_instances()` returns a populated version/tag and an empty instance. `RGWBucketEncryptionConfig::generate_test_instances()` returns KMS with bucket key enabled, AES256, and default instances.

## Control flow
Dencoder tests call these static generators to produce representative values for encode/decode round-trip verification.

## State and persistence
No runtime state is persisted here. The file supports persistence compatibility by supplying test samples for encoded classes.

## Dependencies and integration points
Includes many RGW type headers so dencoder can instantiate encoders. The current concrete functions relate to object versions and bucket encryption config.

## Risks and test signals
The sample set is intentionally small. Risks are missing coverage for newer encoded fields or edge values. Tests should ensure these generated instances round-trip and should add samples when `RGWBucketEncryptionConfig` or `obj_version` encoding evolves.
