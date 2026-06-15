# Optimized First-Pass Research Targets

Generated from `manifests/research_targets.tsv`.

This is the deduplicated first-pass set for studying distributed
filesystems on top of OS/filesystem ground truth. It intentionally keeps
C/C++ OS, protocol, and data-path source ahead of Rust/Go/Java systems,
while retaining representative userspace distributed designs in Go, Java,
Rust, and Python where they are materially different.

| Priority | Source | Level | Kind | Languages | OS fit | Rationale |
|---|---|---|---|---|---|---|
| P0 | `openzfs` | L1 local COW filesystem/pool | local-fs | C | linux,bsd | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `beegfs` | L3 distributed/parallel filesystem | distributed-fs | C,C++ | linux-first | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `ceph` | L3 distributed/parallel filesystem | distributed-fs | C++ | linux-first; clients on linux/macos/windows exist but CephFS kernel path is linux-first | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `glusterfs` | L3 distributed/parallel filesystem | distributed-fs | C | linux-first | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `lustre-release` | L3 distributed/parallel filesystem | distributed-fs | C | linux-first | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `moosefs` | L3 distributed/parallel filesystem | distributed-fs | C | linux-first | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `btrfs-progs` | L1 local filesystem/tools | local-fs | C | linux | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `e2fsprogs` | L1 local filesystem/tools | local-fs | C | linux | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `xfsprogs` | L1 local filesystem/tools | local-fs | C | linux | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `linux` | L0 OS VFS/kernel | os-fs | C | linux | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `fio` | L6 validation/benchmark/fuzzing | test-tool | C | linux-first | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `ltp` | L6 validation/benchmark/fuzzing | test-tool | C,Shell | linux-first | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `xfstests` | L6 validation/benchmark/fuzzing | test-tool | Shell,C | linux-first | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `libfuse` | L2 user/network filesystem | network/user-fs | C | linux,macos,windows-via-ports | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `nfs-ganesha` | L2 user/network filesystem | network/user-fs | C | linux,macos,windows-via-ports | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `nfs-utils` | L2 user/network filesystem | network/user-fs | C | linux,macos,windows-via-ports | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P0 | `samba` | L2 user/network filesystem | network/user-fs | C,Python | linux,macos,windows-via-ports | First-pass source: core OS/protocol/distributed FS path or mandatory validation gate. |
| P1 | `cryptsetup` | L1 block/storage substrate | block-substrate | C | linux | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `lvm2` | L1 block/storage substrate | block-substrate | C | linux | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `util-linux` | L1 block/storage substrate | block-substrate | C | linux | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `bcachefs` | L1 local COW filesystem/pool | local-fs | C | linux,bsd | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `bcachefs-tools` | L1 local COW filesystem/pool | local-fs | C | linux,bsd | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `alluxio` | L3 distributed/parallel filesystem | distributed-fs | Java | linux,macos,windows userspace | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `coda` | L3 distributed/parallel filesystem | distributed-fs | C,C++ | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `eos` | L3 distributed/parallel filesystem | distributed-fs | C++ | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `hadoop` | L3 distributed/parallel filesystem | distributed-fs | Java | linux,macos,windows userspace | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `juicefs` | L3 distributed/parallel filesystem | distributed-fs | Go | linux,macos,windows userspace/FUSE | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `openafs` | L3 distributed/parallel filesystem | distributed-fs | C | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `orangefs` | L3 distributed/parallel filesystem | distributed-fs | C | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `seaweedfs` | L3 distributed/parallel filesystem | distributed-fs | Go | linux,macos,windows userspace/FUSE | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `xrootd` | L3 distributed/parallel filesystem | distributed-fs | C++ | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `erofs-utils` | L1 local filesystem/tools | local-fs | C | linux | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `f2fs-tools` | L1 local filesystem/tools | local-fs | C | linux | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `apache-ozone` | L4 object-store adjacent | object-store-adjacent | Java | linux,macos,windows userspace | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `daos` | L4 object-store adjacent | object-store-adjacent | C,C++ | linux,macos,windows-server/userspace | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `garage` | L4 object-store adjacent | object-store-adjacent | Rust | linux,macos,windows userspace | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `minio` | L4 object-store adjacent | object-store-adjacent | Go | linux,macos,windows userspace | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `openstack-swift` | L4 object-store adjacent | object-store-adjacent | Python | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `rustfs` | L4 object-store adjacent | object-store-adjacent | Rust | linux,macos,windows userspace | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `dragonflybsd` | L0 OS VFS/kernel | os-fs | C | bsd | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `freebsd-src` | L0 OS VFS/kernel | os-fs | C | bsd | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `illumos-gate` | L0 OS VFS/kernel | os-fs | C | illumos/solaris | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `netbsd-src` | L0 OS VFS/kernel | os-fs | C | bsd | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `openbsd-src` | L0 OS VFS/kernel | os-fs | C | bsd | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `xnu` | L0 OS VFS/kernel | os-fs | C,C++ | macos/darwin | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `fscrypt` | L6 security/integrity semantics | security/integrity | Go | linux | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `fsverity-utils` | L6 security/integrity semantics | security/integrity | C | linux | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `blktests` | L6 validation/benchmark/fuzzing | test-tool | Shell | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `ior` | L6 validation/benchmark/fuzzing | test-tool | C | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `pjdfstest` | L6 validation/benchmark/fuzzing | test-tool | Shell,C | linux-first | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `cifs-utils` | L2 user/network filesystem | network/user-fs | C | linux,macos,windows-via-ports | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `libnfs` | L2 user/network filesystem | network/user-fs | C | linux,macos,windows-via-ports | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `dokany` | L0/L1 public Windows FS stack | os-fs | C,C++ | windows | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `reactos` | L0/L1 public Windows FS stack | os-fs | C,C++ | windows-compatible | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `winbtrfs` | L0/L1 public Windows FS stack | os-fs | C | windows | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `windows-driver-samples` | L0/L1 public Windows FS stack | os-fs | C,C++ | windows | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |
| P1 | `winfsp` | L0/L1 public Windows FS stack | os-fs | C | windows | Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison. |

Rows marked `support`, `dedup`, and `defer` remain in
`manifests/research_targets.tsv` so the exclusion rationale is auditable.
