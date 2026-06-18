# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config.go

## Purpose
This file provides OSD configuration helpers for networking and encryption device naming/key generation.

## Important APIs, Types, And Functions
`osdOnSDNFlag(network)` returns Ceph daemon args needed when OSDs run on pod networking. `encryptionKeyPath()` returns the path to the LUKS key under `/etc/ceph`. `EncryptionDMName(pvcName, blockType)` and `EncryptionDMPath(pvcName, blockType)` derive dm-crypt mapper names and paths. `encryptionBlockDestinationCopy(mountPath, blockType)` builds temporary copy paths for block files. `GenerateDmCryptKey()` returns a base64-encoded 128-byte random key.

## Control Flow And State
The file is mostly pure helpers. `osdOnSDNFlag` appends `--ms-learn-addr-from-peer=false` when the network is not host networking, avoiding incorrect peer-learned bind addresses on SDN. `GenerateDmCryptKey` calls `mgr.GenerateRandomBytes` and base64 encodes the result. No Kubernetes or Ceph persistent state is modified here.

## Dependencies And Integration Points
The code depends on CephCluster network specs, OSD config constants such as encryption key filename and block names from nearby package files, operator config paths, and manager random byte generation. It integrates with OSD prepare/activate paths that need consistent encrypted device and key file naming.

## Risks And Test Signals
Risks are mostly compatibility: changing mapper name/path formats would break existing encrypted OSD activation, and network flag behavior affects OSD connectivity on SDN. `config_test.go` covers SDN flag selection, encryption key path, temporary block copy paths, and dm-crypt name/path formatting. Random key length/encoding is not covered in the listed tests.
