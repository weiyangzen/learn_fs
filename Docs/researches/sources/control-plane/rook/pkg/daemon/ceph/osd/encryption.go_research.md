# sources/control-plane/rook/pkg/daemon/ceph/osd/encryption.go

This file implements dm-crypt/LUKS support for OSD devices and KMS key injection into ceph-volume.

Device operations include `CloseEncryptedDevice()`, `RemoveEncryptedDevice()`, `openEncryptedDevice()`, `dmsetupVersion()`, `setLUKSLabelAndSubsystem()`, `dumpLUKS()`, and `isCephEncryptedBlock()`. Key-slot management includes `removeEncryptionKeySlot()`, `ensureEncryptionKey()`, and `addEncryptionKey()`, all using temporary passphrase files and `cryptsetup` commands with timeouts. `addEncryptionKey()` handles full slots by checking if the desired key already matches, removing the old slot if needed, and retrying.

`setKEKinEnv()` reconstructs KMS config from environment variables, adds IBM API key from env, reads KMIP cert/key files from `/etc/kmip`, initializes a KMS config, fetches the key for the PVC name, and sets the ceph-volume encrypted-key environment variable. LUKS labels store `ceph_fsid=<fsid>` and `pvc_name=<pvc>` metadata for later ownership detection.

State includes dm devices, LUKS headers/labels/key slots, temporary passphrase files, KMS secrets, and process environment. Risks include parsing human `cryptsetup luksDump` output due to missing JSON support, temporary secret handling, env-dependent KMS reconstruction, and recursive key-add retry. `encryption_test.go` covers core command handling and FSID detection.
