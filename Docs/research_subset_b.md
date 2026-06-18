# Research Subset B: User, Network, Distributed, Object, Cloud-Native, Testing, Security, Sync, Compression, and Storage Engines

## Scope

This subset covers the `learn_fs` source trees centered on FUSE/user-mode filesystems, network filesystem clients and servers, distributed filesystems, object stores, Kubernetes storage control planes, cloud-native snapshotters and image filesystems, filesystem test tools, security/integrity tooling, sync/backup systems, compression libraries, and storage-engine internals.

Code-only line budget: `14,320,143` focus-path lines across `86` default-counted source trees.

Complete source-tree coverage in this subset: `142` source trees.

## Deduplication

No source tree is deduplicated out of this two-way `learn_fs` split. The subset A and subset B plans together cover every row in `manifests/sources.tsv` exactly once.

Line budgets use `scripts/source_inventory.py --tier all --target-set default-count --scope focus-paths`; source trees with `default_count=no` remain included for research planning even when they do not contribute to the budget total.

## Included Source Trees

- `sources/user-network-fs/libfuse`
- `sources/user-network-fs/sshfs`
- `sources/user-network-fs/go-fuse`
- `sources/user-network-fs/bazil-fuse`
- `sources/user-network-fs/pyfuse3`
- `sources/user-network-fs/fusepy`
- `sources/user-network-fs/s3fs-fuse`
- `sources/user-network-fs/gcsfuse`
- `sources/user-network-fs/blobfuse2`
- `sources/user-network-fs/mergerfs`
- `sources/user-network-fs/nfs-utils`
- `sources/user-network-fs/nfs-ganesha`
- `sources/user-network-fs/libnfs`
- `sources/user-network-fs/go-nfs`
- `sources/user-network-fs/samba`
- `sources/user-network-fs/cifs-utils`
- `sources/user-network-fs/ksmbd-tools`
- `sources/user-network-fs/libsmb2`
- `sources/user-network-fs/impacket`
- `sources/user-network-fs/smbj`
- `sources/user-network-fs/smblibrary`
- `sources/user-network-fs/davfs2`
- `sources/user-network-fs/rclone`
- `sources/distributed-fs/ceph`
- `sources/distributed-fs/ceph-client`
- `sources/distributed-fs/glusterfs`
- `sources/distributed-fs/lustre-release`
- `sources/distributed-fs/beegfs`
- `sources/distributed-fs/beegfs-rust`
- `sources/distributed-fs/beegfs-go`
- `sources/distributed-fs/beegfs-protobuf`
- `sources/distributed-fs/moosefs`
- `sources/distributed-fs/lizardfs`
- `sources/distributed-fs/orangefs`
- `sources/distributed-fs/hadoop`
- `sources/distributed-fs/alluxio`
- `sources/distributed-fs/juicefs`
- `sources/distributed-fs/seaweedfs`
- `sources/distributed-fs/openafs`
- `sources/distributed-fs/coda`
- `sources/distributed-fs/xrootd`
- `sources/distributed-fs/eos`
- `sources/distributed-fs/tahoe-lafs`
- `sources/distributed-fs/ipfs-kubo`
- `sources/object-store/minio`
- `sources/object-store/minio-mc`
- `sources/object-store/openstack-swift`
- `sources/object-store/apache-ozone`
- `sources/object-store/daos`
- `sources/object-store/garage`
- `sources/object-store/rustfs`
- `sources/control-plane/rook`
- `sources/control-plane/longhorn`
- `sources/control-plane/ceph-csi`
- `sources/control-plane/beegfs-csi-driver`
- `sources/control-plane/juicefs-csi-driver`
- `sources/control-plane/csi-spec`
- `sources/control-plane/mayastor`
- `sources/control-plane/csi-driver-nfs`
- `sources/control-plane/csi-driver-smb`
- `sources/control-plane/csi-driver-iscsi`
- `sources/control-plane/longhorn-engine`
- `sources/control-plane/csi-driver-host-path`
- `sources/control-plane/external-snapshotter`
- `sources/control-plane/csi-lib-utils`
- `sources/cloud-native/fuse-overlayfs`
- `sources/cloud-native/overlayfs-tools`
- `sources/cloud-native/fuse-overlayfs-snapshotter`
- `sources/cloud-native/containers-storage`
- `sources/cloud-native/containerd`
- `sources/cloud-native/stargz-snapshotter`
- `sources/cloud-native/nydus`
- `sources/cloud-native/nydus-snapshotter`
- `sources/cloud-native/soci-snapshotter`
- `sources/cloud-native/composefs`
- `sources/cloud-native/composefs-rs`
- `sources/cloud-native/moby`
- `sources/cloud-native/buildkit`
- `sources/cloud-native/cri-o`
- `sources/cloud-native/overlaybd`
- `sources/cloud-native/ostree`
- `sources/test-tools/xfstests`
- `sources/test-tools/xfstests-bld`
- `sources/test-tools/blktests`
- `sources/test-tools/fio`
- `sources/test-tools/ltp`
- `sources/test-tools/pjdfstest`
- `sources/test-tools/crashmonkey`
- `sources/test-tools/filebench`
- `sources/test-tools/fs-mark`
- `sources/test-tools/ior`
- `sources/test-tools/unionmount-testsuite`
- `sources/test-tools/pynfs`
- `sources/test-tools/cthon04`
- `sources/test-tools/kdevops`
- `sources/test-tools/liburing`
- `sources/test-tools/strace`
- `sources/test-tools/lcov`
- `sources/test-tools/stress-ng`
- `sources/test-tools/iozone`
- `sources/security-integrity/fscrypt`
- `sources/security-integrity/fsverity-utils`
- `sources/security-integrity/ecryptfs-utils`
- `sources/security-integrity/gocryptfs`
- `sources/security-integrity/cryfs`
- `sources/security-integrity/encfs`
- `sources/security-integrity/ima-evm-utils`
- `sources/security-integrity/acl`
- `sources/security-integrity/attr`
- `sources/security-integrity/libcap`
- `sources/security-integrity/keyutils`
- `sources/security-integrity/selinux`
- `sources/security-integrity/audit-userspace`
- `sources/sync-backup/rsync`
- `sources/sync-backup/syncthing`
- `sources/sync-backup/restic`
- `sources/sync-backup/borg`
- `sources/sync-backup/kopia`
- `sources/sync-backup/git-annex`
- `sources/sync-backup/casync`
- `sources/sync-backup/unison`
- `sources/sync-backup/git-lfs`
- `sources/sync-backup/git-crypt`
- `sources/sync-backup/bup`
- `sources/compression/zstd`
- `sources/compression/xz`
- `sources/compression/lz4`
- `sources/compression/zlib`
- `sources/test-tools/syzkaller`
- `sources/storage-engines/rocksdb`
- `sources/storage-engines/leveldb`
- `sources/storage-engines/pebble`
- `sources/storage-engines/badger`
- `sources/storage-engines/wiredtiger`
- `sources/storage-engines/sqlite`
- `sources/storage-engines/lmdb`
- `sources/storage-engines/foundationdb`
- `sources/storage-engines/tikv`
- `sources/storage-engines/raft-engine`
- `sources/user-network-fs/macfuse`
- `sources/user-network-fs/libtirpc`
- `sources/user-network-fs/rpcbind`

## Why This Group

This subset is the filesystem integration and data-management lane. It keeps user-space filesystem APIs, network filesystem protocols, distributed metadata/data paths, object-store layers, CSI/control-plane implementations, container snapshotters, testing/fuzzing workloads, integrity/security tools, backup/sync systems, compression dependencies, and embedded storage engines together.

The full default-counted `learn_fs` focus-path corpus is about `29,576,995` code-like lines. A two-way split targets about `14,788,498` lines per subset; this subset is about `14,320,143` lines.

## Research Cron Notes

- Use the `research-cron-builder` code-only scope.
- Preserve source-tree-aligned final artifacts under `Docs/researches/<source_path>_research.md`.
- Keep grouped prompts at or below `262144` bytes unless the final runner explicitly changes `GROUP_LIMIT_BYTES`.
- Chunk oversized files instead of sampling them.
- Do not mark the subset complete until per-file and folder-level indexes are OK.
