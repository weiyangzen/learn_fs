# sources/control-plane/rook/pkg/daemon/ceph/osd/encryption_test.go

This file tests the LUKS/dm-crypt command helpers with mocked executor behavior.

`TestCloseEncryptedDevice` validates `cryptsetup --verbose luksClose`. `TestRemoveEncryptionKeySlot` checks successful slot removal and ignored "Keyslot N is not active" errors. `TestEnsureEncryptionKey` verifies the `luksChangeKey` probe returns true on success and false without error when output says no key is available for the passphrase. `TestAddEncryptionKey` covers empty slots, full slots containing the desired key, and full slots requiring removal plus recursive add. `TestDmsetupVersion` validates `dmsetup version`. `TestIsCephEncryptedBlock` parses a realistic LUKS dump fixture and distinguishes matching versus different Ceph FSIDs.

State is mocked command output and temporary passphrase files created by the implementation. Integration points include Rook's mock executor and timeout command path. Gaps include no tests for KMS environment loading, KMIP file reads, LUKS label setting, open/remove dm-device failures, or temporary file permission inspection. The tests strongly document accepted cryptsetup output strings used for error classification.
