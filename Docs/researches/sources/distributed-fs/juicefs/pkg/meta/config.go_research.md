# sources/distributed-fs/juicefs/pkg/meta/config.go

## Purpose

`config.go` defines client runtime metadata configuration and persistent volume format metadata for JuiceFS. It also implements compatibility checks, secret redaction, and encryption/decryption of sensitive format fields before storage or display.

## Important APIs And Types

`Config` is the in-memory client/mount configuration. Important fields include retry/delete limits, case-insensitive mode, read-only mode, background-job disablement, open-cache settings, heartbeat, mount/subdir identity, atime mode, directory-stat flush period, session id, directory sorting, fast statfs, and network-interface selection. `DefaultConf` sets conservative defaults: 10 retries, max 2 deletes, 12 second heartbeat, `NoAtime`, and 1 second dir-stat flushes. `SelfCheck` normalizes dangerous heartbeat values and warns when object deletion is disabled.

`Format` is persistent volume configuration loaded from metadata storage. It records volume identity, storage backend and credentials, object layout parameters, capacity/inode limits, encryption settings, bandwidth limits, trash retention, metadata version, client version constraints, directory stats, user/group quota, ACL enablement, Ranger settings, change log limits, and Kerberos config. `String` returns JSON with secrets redacted through `RemoveSecret`.

`Format.update` compares a new format with an existing one. Without `force`, it rejects changes to name, block size, compression, shards, hash prefix, and metadata version. UUID changes are special: when only UUID differs, the method decrypts the new secrets using the new UUID, sets the old UUID, and re-encrypts so secret ciphertext stays decryptable under the persisted UUID. With `force`, it allows overwrite and logs a warning.

`CheckVersion` and `CheckCliVersion` enforce metadata and client version compatibility using `pkg/version`. `newCipher`, `Encrypt`, and `Decrypt` implement AEAD encryption for `SecretKey`, `SessionToken`, and `EncryptKey`. `newCipher` uses SM4-GCM with an SM3 KDF for `object.SM4GCM`, and otherwise AES-GCM with an MD5-derived key from the UUID.

## Control Flow

Encryption is idempotent: `Encrypt` returns immediately if `KeyEncrypted` is already true or there are no secrets. Otherwise it creates a cipher from `EncryptAlgo` and `UUID`, generates a random nonce per field, seals the plaintext, prepends nonce to ciphertext, base64-encodes it, and marks `KeyEncrypted`. `Decrypt` is similarly guarded by `KeyEncrypted`; it base64-decodes each field, opens the AEAD with the nonce prefix, restores plaintext, and clears `KeyEncrypted`. If a secret has been redacted to `"removed"`, decryption returns an actionable error asking the user to correct it via config.

## State And Persistence Behavior

`Config` is process-local, but `Format` is serialized to metadata storage and therefore acts as a persistent volume contract. `RemoveSecret` intentionally destroys in-memory secret values for safe display; after redaction, `Decrypt` cannot recover them. `Encrypt` mutates the `Format` in place and uses random nonces, so ciphertext changes across encryptions even for the same plaintext.

## Dependencies And Integration Points

The file integrates with object encryption constants (`pkg/object`), JuiceFS semantic version helpers, package logging, Go crypto packages, JSON serialization, and third-party GM/T SM3/SM4 implementations. Other metadata files call these methods during `Init`, `Load`, config update, mount setup, and CLI display paths.

## Risks And Test Signals

The UUID is the encryption key source, so UUID-change handling is sensitive. Reordering `Decrypt`/UUID assignment/`Encrypt` in `update` can make stored credentials unrecoverable. AES uses MD5 as a key derivation shortcut, which is compatibility-sensitive rather than modern KDF design. `Decrypt` assumes decoded buffers are at least nonce-sized; malformed stored ciphertext could panic if not guarded elsewhere. Tests in `config_test.go` cover redaction, round trips across supported algorithms, and UUID key-conflict update behavior.
