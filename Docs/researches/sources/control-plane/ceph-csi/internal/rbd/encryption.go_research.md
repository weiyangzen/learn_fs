# sources/control-plane/ceph-csi/internal/rbd/encryption.go

## Purpose
Implements RBD encryption configuration, metadata migration, KMS integration, DEK storage through image metadata, LUKS device open/format helpers, and block-encryption key rotation.

## Important APIs, Types, And Functions
`rbdEncryptionState` models unknown, prepared, and encrypted states. Metadata keys include current and legacy encryption/DEK keys plus LUKS2 header-size metadata. Core helpers are `getLuksHeaderSizeMetadata`, `checkRbdImageEncrypted`, `ensureEncryptionMetadataSet`, `isBlockEncrypted`, `isFileEncrypted`, `IsFileEncrypted`, `setupBlockEncryption`, `copyEncryptionConfig`, `repairEncryptionConfig`, `encryptDevice`, `openEncryptedDevice`, `initKMS`, `parseCipherOptions`, `ParseEncryptionOpts`, `configureBlockEncryption`, `configureFileEncryption`, `StoreDEK`, `FetchDEK`, `RemoveDEK`, `GetEncryptionPassphraseSize`, and `RotateEncryptionKey`.

## Control Flow
Creation-time parsing starts with `ParseEncryptionOpts`, which interprets `encrypted`, KMS ID, and optional encryption type, then `initKMS` configures block or file encryption. Block encryption may parse cryptsetup cipher/key/integrity/sector options and uses KMS plus optional RBD metadata DEK store. `setupBlockEncryption` stores a new passphrase and marks metadata as prepared. Node/device paths use `encryptDevice` to format and mark encrypted, and `openEncryptedDevice` to map a LUKS device. Clone/snapshot flows use `copyEncryptionConfig` or `repairEncryptionConfig` to copy passphrases/configuration and metadata. `RotateEncryptionKey` validates encrypted state, opens ioctx, takes a RADOS lock based on object UUID, adds a backup LUKS key, generates/stores a new key, and removes the backup slot.

## State And Persistence
Persistent state lives in KMS backends, RBD image metadata (`encrypted`, DEK, LUKS header size), LUKS slots on the mapped device, and temporary RADOS locks for key rotation. Legacy metadata is migrated with `MigrateMetadata`. `RemoveDEK` intentionally leaves metadata untouched because image deletion typically removes it.

## Dependencies And Integration Points
Depends on KMS APIs, `util.VolumeEncryption`, cryptsetup wrappers, RBD metadata helpers, RADOS lock helpers, package mounter state, and wait-for-device path helpers. Controller create/clone/snapshot paths call KMS initialization and config copy, while node paths use device encryption/open helpers.

## Risks And Test Signals
Risks include metadata/KMS inconsistency after partial failures, unsupported file-encryption KMS behavior, unsafe key-rotation interruption after KMS update but before LUKS cleanup, mismatched volume IDs in DEK store methods, and LUKS header-size compatibility for older images. `encryption_test.go` covers option parsing and cipher validation but not live KMS, metadata migration, cryptsetup, or rotation.
