# FS Language, Level, OS Fit, And Deduplication Analysis

This document is generated from `manifests/sources.tsv` plus the
first-pass deduplication policy in `scripts/generate_research_targets.py`.

## Language Judgment

For filesystem work, language priority depends on the layer.

- `C`: still the first language for OS VFS, kernel filesystems, page cache,
  block layer, syscall ABI, mount helpers, fsck/mkfs/repair tools, and
  mature network protocols. It is the strongest baseline when the target
  is large-scale, hot-path, OS-integrated filesystem behavior.
- `C++`: strong for large userspace distributed filesystems and object/data
  services where complex metadata, RPC, caching, placement, and recovery
  logic dominate. Ceph, BeeGFS daemons, XRootD/EOS, RocksDB-style metadata
  engines, and some storage substrates fit here.
- `Rust`: good for new userspace filesystem components, image/snapshotter
  tooling, safety-sensitive daemons, and storage services where ownership
  clarity is valuable. It is not the first route for mature Linux kernel
  filesystem internals, but it is not a detour for well-bounded userspace
  components.
- `Go`: weak fit for kernel/hot-path filesystem internals, but a strong fit
  for distributed service code, metadata servers, object-store interfaces,
  CSI/control-plane, sync/backup, and FUSE/object-backed filesystems when
  network latency and operational complexity dominate CPU instruction cost.

Practical rule: study C/C++ data paths first, then Rust/Go/Java systems as
userspace distributed design alternatives. For mixed-language projects,
read the data path before management glue.

## Mixed-Language Priority

| Project | Priority inside project | Reason |
|---|---|---|
| Ceph | C++ MDS/client/OSD/RADOS first; Python/admin later | Core distributed FS and object paths are C++. |
| BeeGFS | C kernel client and C++ services first; Go/Rust management later | The filesystem behavior is in client/module/services. |
| Samba | C SMB/VFS modules first; Python tests/build later | Protocol and VFS behavior are C. |
| Lustre | C client/server/LNet first; scripts/tests later | Kernel/client/server hot paths are C. |
| Hadoop/Alluxio/Ozone | Java core first; native bits later | The system model is JVM userspace, not OS kernel FS. |
| JuiceFS/SeaweedFS/MinIO | Go core first, but after C/C++ FS baselines | Good distributed userspace systems; not kernel-level FS references. |
| DAOS | C/C++ engine/VOS first; Python/tools later | The storage engine and distributed object paths are native. |
| Nydus/composefs-rs/Mayastor/Garage/RustFS | Rust core first, but as userspace/container/object layer | Useful modern safety-oriented systems, secondary to OS FS internals. |

## FS Level Marking

- `L0 OS VFS/kernel`: Linux, BSDs, illumos, XNU, ReactOS/public Windows samples.
- `L1 local filesystem/tools`: ext/XFS/Btrfs/F2FS/EROFS/ZFS/bcachefs and mkfs/fsck/repair tooling.
- `L2 user/network filesystem`: FUSE, NFS, SMB/CIFS, WebDAV, object-backed mounts.
- `L3 distributed/parallel filesystem`: CephFS, GlusterFS, Lustre, BeeGFS, MooseFS, OrangeFS, HDFS, Alluxio, JuiceFS, SeaweedFS, AFS/Coda, XRootD/EOS.
- `L4 object/container/virtual substrate`: MinIO, Swift, Ozone, DAOS, Garage, RustFS, container snapshotters, QEMU/SPDK/NBD.
- `L5 control plane`: CSI, Rook, Longhorn, Kubernetes storage glue.
- `L6 validation/support`: xfstests, fio, LTP, fscrypt/fsverity, sync/backup, compression, storage engines.

## OS Fit

- Linux: primary target for kernel FS, local FS tools, NFS/SMB server paths,
  and most distributed FS clients/servers.
- macOS: realistic for userspace clients, FUSE/macFUSE, object-backed mounts,
  Go/Java/Rust services, and XNU VFS comparison. It is not the main target
  for Linux-first kernel/distributed FS internals.
- Windows: realistic for WinFsp/Dokany/public driver samples, user-mode
  clients, Go/Java/Rust services, and ReactOS comparison. Linux remains the
  primary platform for most open distributed FS kernel clients.

## Optimized First-Pass Result

- total source rows analyzed: 214
- keep/count now: 57
- support but do not count now: 65
- deduplicated against stronger source: 18
- deferred: 74
- measured optimized focus-path checkouts: 57
- missing optimized checkouts: 0
- measured optimized code-like lines: 21263025

Kept rows by category:

| Category | Count |
|---|---:|
| block-storage | 3 |
| cow-pools | 3 |
| distributed-fs | 14 |
| local-fs | 5 |
| object-store | 6 |
| os-vfs | 7 |
| security-integrity | 2 |
| test-tools | 6 |
| user-network-fs | 6 |
| windows-public | 5 |

Kept rows by primary language label:

| Primary language label | Count |
|---|---:|
| C | 32 |
| C++ | 3 |
| C,C++ | 7 |
| C,Python | 1 |
| C,Shell | 1 |
| Go | 4 |
| Java | 3 |
| Python | 1 |
| Rust | 2 |
| Shell | 1 |
| Shell,C | 2 |

The full row-level decision table is `manifests/research_targets.tsv`.
