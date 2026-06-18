# sources/control-plane/ceph-csi/internal/csi-addons/rbd/encryptionkeyrotation.go

Purpose: CSI-addons encryption key rotation controller for RBD volumes.

Important APIs/types/functions: `EncryptionKeyRotationServer` embeds the unimplemented CSI-addons encryption key rotation controller, stores driver instance and volume lock, and exposes `NewEncryptionKeyRotationServer()`, `RegisterService()`, and `EncryptionKeyRotate()`.

Control flow: `EncryptionKeyRotate()` validates volume ID, acquires the per-volume lock, creates an RBD manager from driver instance and request secrets, resolves the RBD volume by CSI ID, maps not-found/pool-not-found errors to `NotFound`, calls `RotateEncryptionKey()`, and returns an empty success response.

State and persistence: backend state is the RBD volume encryption key/passphrase metadata managed by lower RBD layers and KMS. This file only coordinates locking and RPC error mapping. Manager and volume handles are destroyed with defers.

Dependencies and integration points: depends on CSI-addons encryptionkeyrotation protobufs, RBD manager/volume APIs, RBD error sentinels, common ID validation, IDLocker, and logging. It is advertised by RBD CSI-addons identity when running as a node server.

Risks: no explicit check that the volume is encrypted before invoking lower-level rotation. Lock contention maps to `Aborted`. Credentials and KMS errors collapse mostly to `Internal`, so callers need logs for detail. Correctness depends on `RotateEncryptionKey()` atomicity.

Test signals: no direct tests in this item. Useful coverage would mock manager/volume lookups, lock contention, invalid IDs, not-found mapping, and rotation failures.
