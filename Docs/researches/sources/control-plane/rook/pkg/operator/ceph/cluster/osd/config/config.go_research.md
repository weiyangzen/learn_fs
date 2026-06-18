# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config/config.go

## Purpose
This package file defines structured OSD store configuration parsed from string maps, plus JSON-facing types for configured devices.

## Important APIs, Types, And Functions
Constants define keys such as `walSizeMB`, `databaseSizeMB`, `osdsPerDevice`, `encryptedDevice`, `metadataDevice`, `deviceClass`, `initialWeight`, and `primaryAffinity`. `StoreConfig` holds WAL/database sizes, OSDs per device, encryption flag, metadata device, device class, initial weight, primary affinity, and store type. `IsValidStoreType()` accepts BlueStore and BlueStoreRDR. `GetStoreFlag()` returns `--<storeType>`. `NewStoreConfig()` defaults `OSDsPerDevice` to 1. `ToStoreConfig(config)` parses a string map into a `StoreConfig`. `MetadataDevice(config)` extracts just the metadata device. `ConfiguredDevice` pairs a device ID with a store config.

## Control Flow And State
`ToStoreConfig` iterates over arbitrary map order and switches on known keys. Integer parsing ignores invalid values by returning zero; `OSDsPerDevice` only updates when the parsed value is positive, preserving the default of 1 for absent, invalid, or nonpositive values. Encryption is true only for exact string `"true"`. Unknown keys are ignored. No persistent state is changed; the struct is passed onward to OSD provisioning logic.

## Dependencies And Integration Points
The file depends on Ceph API store type constants and Go JSON tags. It integrates with OSD discovery/provisioning code that accepts device configuration from CRD fields or device maps.

## Risks And Test Signals
The lenient parsing model avoids hard failures but can silently turn invalid numeric values into zero or ignore typos. Store type validation is narrow and must stay aligned with supported Ceph/Rook store types. No direct test file for this subpackage is listed in the work item; coverage may exist elsewhere. The adjacent `osd/config_test.go` does not exercise this package.
