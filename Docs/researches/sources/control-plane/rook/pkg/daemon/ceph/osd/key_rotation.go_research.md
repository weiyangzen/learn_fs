# sources/control-plane/rook/pkg/daemon/ceph/osd/key_rotation.go

This file implements online key-encryption-key rotation for encrypted OSD devices.

`RotateKeyEncryptionKey()` takes a KMS config, secret name, and device paths. It fetches the current key from KMS and rejects empty values. It first ensures the current key is also present in LUKS slot `1` on every device, then generates a new dm-crypt key with `oposd.GenerateDmCryptKey()`. For each device, it removes slot `0` using the current key and adds the new key to slot `0`. It then updates the KMS secret to the new key, fetches it back for verification, and finally removes the old key from slot `1` on every device using the new key.

State changes span LUKS key slots on all device paths and the external KMS secret. The sequence is designed to keep an unlockable key available during rotation: current key in slot 1, new key in slot 0, then old slot cleanup after KMS verification.

Risks include non-atomic multi-device rotation, failures after some devices or KMS state have changed, reliance on `addEncryptionKey()` idempotency, and no direct unit test in this work item for rollback or partial failure behavior. Integration points are `encryption.go` slot helpers and KMS `GetSecret`/`UpdateSecret`.
