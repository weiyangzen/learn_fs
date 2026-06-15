# Agent 07: 云原生/容器/虚拟化文件系统与存储源码候选方案

日期：2026-06-15

根目录：`/Users/wangweiyang/GitHub/learn_fs`

目标：构建“只看源码”的文件系统/分布式文件系统研究仓库，Agent 07 负责云原生、容器、虚拟化文件系统与存储方向。完整源码计数目标为 2000 万到 2 亿行。该方向建议以完整上游仓库为主要收录单元，源码计数时排除 `.git/`、构建产物、vendor、node_modules、docs、examples 中的非源码资产和生成文件。

## 收录边界

必收标准：

- 直接实现内核文件系统、FUSE、OverlayFS、NBD、virtiofs、块层、container snapshotter、镜像懒加载、只读镜像文件系统、SPDK 或相关用户态块存储路径。
- 直接承载容器层、镜像层、snapshotter、mount、verity、EROFS、RAFS、stargz、SOCI、composefs 等核心数据路径。
- CSI 只收能体现真实存储实现或文件/块协议挂载逻辑的项目，不扩展为云厂商 CSI 驱动大全。

不建议收录：

- 只有文档、Helm chart、Terraform、部署样例的仓库。
- 只提供 API glue 的 Kubernetes sidecar，除非后续要专门研究 CSI 控制面。
- 大量语言运行时、发行版打包仓库、镜像构建仓库。
- 与本 Agent 范围重叠但应由分布式文件系统 Agent 负责的完整 Ceph、GlusterFS、MooseFS、Lustre 等大型分布式 FS 主仓库。这里最多保留与 CSI 或容器化接入相关的边界仓库。

代码量策略：

- `must` 完整收录预计可达到约 4500 万到 7000 万源码行，主要体量来自 Linux、QEMU、SPDK、containerd、containers/storage、Nydus、snapshotter 与 CSI/云原生存储实现。
- 如果 Linux 只做稀疏 checkout 到 `fs/overlayfs`、`fs/fuse`、`drivers/block/nbd.c` 等关注路径，总量可能掉到 2000 万行以下，不建议作为主方案。
- `optional` 扩展后预计在约 6000 万到 1 亿源码行区间，仍低于 2 亿行上限。

## 建议目录结构

```text
/Users/wangweiyang/GitHub/learn_fs/
  README.md
  Docs/
    agent07-cloud-native-virtual-storage.md
    agent07-repos.yaml
  scripts/
    clone-agent07.sh
    audit-agent07-remotes.sh
    count-source-loc.sh
  src/
    00-kernel/
      linux/
      erofs-utils/
      fsverity-utils/
    01-fuse-overlay/
      libfuse/
      fuse-overlayfs/
      overlayfs-tools/
      fuse-overlayfs-snapshotter/
    02-container-storage/
      containerd/
      containers-storage/
      moby/
      buildkit/
      cri-o/
    03-image-snapshotters/
      stargz-snapshotter/
      nydus/
      nydus-snapshotter/
      soci-snapshotter/
      overlaybd/
      accelerated-container-image/
    04-composefs-readonly/
      composefs/
      composefs-rs/
    05-virtio-qemu/
      qemu/
      virtiofsd/
      kata-containers/
      rust-vmm-vhost-device/
    06-block-nbd-spdk/
      spdk/
      nbd/
      nbdkit/
      libnbd/
    07-csi-direct/
      csi-spec/
      mayastor/
      ceph-csi/
      csi-driver-nfs/
      csi-driver-smb/
      csi-driver-iscsi/
      csi-driver-host-path/
      longhorn-engine/
  indexes/
    loc-agent07.tsv
    remotes-agent07.tsv
    focus-paths-agent07.tsv
```

目录原则：

- `src/00-kernel` 放内核和内核配套工具。Linux 作为完整源码保留，用 focus path 引导阅读。
- `src/01-fuse-overlay` 放 FUSE 与 OverlayFS 用户态实现、调试和 containerd fuse snapshotter。
- `src/02-container-storage` 放容器运行时和本地镜像/层存储实现。
- `src/03-image-snapshotters` 放远程镜像、懒加载、分块、索引和 snapshotter 实现。
- `src/04-composefs-readonly` 单独放 composefs 及 Rust 实现，便于研究 fs-verity/EROFS/OCI image 的交叉点。
- `src/05-virtio-qemu` 放虚拟化文件系统、QEMU block layer、vhost-user/virtio 相关实现。
- `src/06-block-nbd-spdk` 放用户态块设备、高性能 NVMe/bdev、NBD 协议与工具链。
- `src/07-csi-direct` 只放与文件/块存储实现直接相关的 CSI 项目。

## 必收源码仓库

| 分组 | 仓库 | 目标目录 | 重点源码路径 | 收录理由 |
| --- | --- | --- | --- | --- |
| Kernel | `torvalds/linux` | `src/00-kernel/linux` | `fs/overlayfs`, `fs/fuse`, `fs/erofs`, `fs/verity`, `drivers/block/nbd.c`, `block`, `drivers/virtio`, `include/uapi/linux` | OverlayFS、virtiofs、NBD、EROFS、fs-verity、内核块层的主实现。必须完整收录以满足源码体量和上下文交叉引用。 |
| Kernel tools | `xiang/erofs-utils` | `src/00-kernel/erofs-utils` | `mkfs`, `dump`, `fsck`, `lib` | EROFS 用户态工具，对 composefs、容器只读镜像和压缩只读 FS 研究有直接价值。 |
| Kernel tools | `fsverity/fsverity-utils` | `src/00-kernel/fsverity-utils` | `programs`, `lib` | fs-verity 用户态工具，composefs 和只读完整性验证路径需要。 |
| FUSE | `libfuse/libfuse` | `src/01-fuse-overlay/libfuse` | `lib`, `include`, `example`, `util` | FUSE 协议与库实现，是 fuse-overlayfs、virtiofsd、用户态 FS 的共同基础。 |
| Overlay user space | `containers/fuse-overlayfs` | `src/01-fuse-overlay/fuse-overlayfs` | `*.c`, `utils`, `tests` | rootless container overlay 的核心实现。 |
| Overlay tools | `kmxz/overlayfs-tools` | `src/01-fuse-overlay/overlayfs-tools` | `overlay`, `diff`, `mount` 相关源码 | OverlayFS 用户态检查/调试工具，虽小但直接补足 progs 侧。 |
| Snapshotter | `containerd/fuse-overlayfs-snapshotter` | `src/01-fuse-overlay/fuse-overlayfs-snapshotter` | snapshotter plugin, mount handling | containerd 接入 fuse-overlayfs 的最直接实现。 |
| Runtime storage | `containerd/containerd` | `src/02-container-storage/containerd` | `core/snapshots`, `plugins`, `mount`, `metadata`, `content`, `images` | containerd content store、snapshotter 框架、overlay snapshotter、镜像 unpack/mount 主线。 |
| Runtime storage | `containers/storage` | `src/02-container-storage/containers-storage` | `drivers/overlay`, `pkg`, `store`, `mount` | Podman/Buildah/CRI-O 的容器层存储实现，overlay、chunked image、composefs 集成路径关键。 |
| Lazy image | `containerd/stargz-snapshotter` | `src/03-image-snapshotters/stargz-snapshotter` | `snapshot`, `fs`, `estargz`, `cmd`, `service` | eStargz 懒加载 snapshotter 代表实现。 |
| Lazy image | `dragonflyoss/nydus` | `src/03-image-snapshotters/nydus` | `storage`, `rafs`, `daemon`, `service`, `api` | Nydus/RAFS 镜像文件系统与用户态 daemon 的核心实现。 |
| Lazy image | `containerd/nydus-snapshotter` | `src/03-image-snapshotters/nydus-snapshotter` | snapshotter, converter, metadata | containerd 接入 Nydus 的核心 glue 与数据路径。 |
| Lazy image | `awslabs/soci-snapshotter` | `src/03-image-snapshotters/soci-snapshotter` | `fs`, `snapshot`, `soci`, `ztoc`, `cmd` | SOCI 索引与 lazy pulling 实现，和 stargz/nydus 对照价值高。 |
| Read-only image FS | `composefs/composefs` | `src/04-composefs-readonly/composefs` | `libcomposefs`, `tools`, `mkcomposefs` | composefs C 实现，容器只读层、verity、lower data composition 的关键项目。 |
| Read-only image FS | `composefs/composefs-rs` | `src/04-composefs-readonly/composefs-rs` | Rust crates, `composefs` tools | composefs Rust 实现和新方向，需与 C 版并读。 |
| Virtualization | `qemu-project/qemu` | `src/05-virtio-qemu/qemu` | `block`, `hw/block`, `hw/virtio`, `include/block`, `tests/qemu-iotests` | QEMU block layer、virtio block、virtio-scsi、vhost-user 接口和虚拟化存储主线。 |
| Virtualization | `virtio-fs/virtiofsd` | `src/05-virtio-qemu/virtiofsd` | daemon, sandbox, passthrough, virtio queue handling | 独立 Rust virtiofsd 上游，是现代 virtiofs 用户态服务端主线。 |
| User-space block | `spdk/spdk` | `src/06-block-nbd-spdk/spdk` | `lib/bdev`, `lib/blob`, `lib/nvme`, `lib/vhost`, `lib/nbd`, `module/bdev`, `app` | SPDK 用户态块栈、bdev、BlobFS、vhost、NBD、NVMe-oF，是虚拟化和云原生高性能块存储核心。 |
| NBD | `NetworkBlockDevice/nbd` | `src/06-block-nbd-spdk/nbd` | server/client tools, protocol handling | Linux NBD 用户态工具和协议实现。 |
| NBD | `nbdkit/nbdkit` | `src/06-block-nbd-spdk/nbdkit` | `server`, `plugins`, `filters`, `common` | NBD 插件化服务端，对镜像、块设备、过滤器研究直接有用。 |
| NBD | `nbdkit/libnbd` | `src/06-block-nbd-spdk/libnbd` | `lib`, `generator`, `copy`, `info` | NBD 客户端库和工具，与 nbdkit 配套。 |
| CSI direct | `container-storage-interface/spec` | `src/07-csi-direct/csi-spec` | `csi.proto`, generated client code | CSI 接口定义。虽偏规范，但 proto 源码是理解驱动边界的最小依赖。 |
| CSI direct | `openebs/mayastor` | `src/07-csi-direct/mayastor` | `io-engine`, `control-plane`, CSI integration | SPDK 在 Kubernetes 中落地的直接实现，和 `spdk/spdk` 必须联读。 |
| CSI direct | `ceph/ceph-csi` | `src/07-csi-direct/ceph-csi` | CephFS/RBD node/controller server, mount/attach logic | CephFS/RBD 的 CSI 接入层；不替代完整 Ceph 源码，但能覆盖容器存储边界。 |
| CSI direct | `kubernetes-csi/csi-driver-nfs` | `src/07-csi-direct/csi-driver-nfs` | NFS mount/provision logic | 文件协议 CSI 驱动，适合作为最小文件卷驱动参考。 |

## 可选源码仓库

| 分组 | 仓库 | 目标目录 | 重点源码路径 | 何时收录 |
| --- | --- | --- | --- | --- |
| Container integration | `moby/moby` | `src/02-container-storage/moby` | `daemon/graphdriver/overlay2`, image/layer code, mount setup | 需要研究 Docker overlay2、graphdriver、镜像层与 containerd 交界时收录。 |
| Build cache | `moby/buildkit` | `src/02-container-storage/buildkit` | snapshot, cache, worker, content store | 需要研究构建缓存、snapshot lease、lazy pull 与 OCI layer 工作流时收录。 |
| Runtime integration | `cri-o/cri-o` | `src/02-container-storage/cri-o` | storage integration, server runtime paths | 需要研究 CRI-O 如何通过 containers/storage 驱动 overlay/composefs 时收录。 |
| Lazy image | `containerd/overlaybd` | `src/03-image-snapshotters/overlaybd` | block based remote image, snapshotter | 需要比较文件级 lazy pull 与块级 lazy image 时收录。 |
| Lazy image | `containerd/accelerated-container-image` | `src/03-image-snapshotters/accelerated-container-image` | image acceleration, conversion, snapshotter pieces | 需要覆盖 containerd 生态中较新的加速镜像实验实现时收录。 |
| Virtualization integration | `kata-containers/kata-containers` | `src/05-virtio-qemu/kata-containers` | virtiofs, shared fs, runtime config, agent mount paths | 需要研究 virtiofs 在安全容器和轻量 VM 中如何接入时收录。 |
| Rust vhost ecosystem | `rust-vmm/vhost-device` | `src/05-virtio-qemu/rust-vmm-vhost-device` | vhost-user device crates | 需要补充 Rust vhost-user 设备生态时收录。 |
| CSI direct | `kubernetes-csi/csi-driver-smb` | `src/07-csi-direct/csi-driver-smb` | SMB mount/provision logic | 需要文件协议 CSI 的 SMB 对照时收录。 |
| CSI direct | `kubernetes-csi/csi-driver-iscsi` | `src/07-csi-direct/csi-driver-iscsi` | iSCSI attach/mount logic | 需要块协议 CSI 的简洁参考时收录。 |
| CSI reference | `kubernetes-csi/csi-driver-host-path` | `src/07-csi-direct/csi-driver-host-path` | node/controller sample implementation | 需要最小 CSI 驱动骨架或测试基线时收录。 |
| Cloud-native block | `longhorn/longhorn-engine` | `src/07-csi-direct/longhorn-engine` | replica, engine, controller, sync agent | 需要研究用户态复制块存储与 Kubernetes 接入时收录。 |
| CSI control plane | `kubernetes-csi/external-snapshotter` | `src/07-csi-direct/external-snapshotter` | snapshot controller, CRD API glue | 只在研究 CSI snapshot 控制面时收录，不作为默认源码主线。 |
| CSI libraries | `kubernetes-csi/csi-lib-utils` | `src/07-csi-direct/csi-lib-utils` | connection helpers, retry, metrics | 只在分析多个 CSI 驱动公共库时收录。 |
| FS tests | `xfs/xfstests-dev` | `src/00-kernel/xfstests-dev` | overlay, generic, nfs, btrfs tests | 如果研究需要行为验证，可收录测试源码，但不计入核心源码清单。 |

## 明确排除或降级

- 完整 `ceph/ceph`：分布式文件系统/对象/块栈主体，体量很大，应由分布式存储 Agent 收录；Agent 07 只保留 `ceph-csi`，除非本方向必须自洽研究 CephFS/RBD 内核外实现。
- 云厂商 CSI 驱动全集：例如 EBS、GCE PD、Azure Disk/File 等，默认不收。它们更多体现云 API 适配，不是文件系统或块栈实现。
- Kubernetes CSI sidecar 全集：`external-provisioner`、`external-attacher`、`node-driver-registrar` 默认不收，除非做 CSI 控制面专题。
- OCI spec、image-spec、distribution-spec：作为阅读参考可链接，但不是源码实现主线，默认不计入源码全集。
- runc/crun：mount namespace 和 rootfs setup 有价值，但不是本 Agent 的核心 FS/storage 实现，可由容器运行时 Agent 或安全容器 Agent 处理。
- libarchive、zstd、lz4、openssl、protobuf 等通用依赖：不作为本仓库独立源码收录，除非某个项目 vendor 进来且源码计数时排除 vendor。

## 遗漏风险

1. OverlayFS kernel/progs 覆盖不足：内核 `fs/overlayfs` 是主实现，但用户态 progs 生态分散且小众，`overlayfs-tools` 不是内核官方项目。后续可通过搜索 `overlayfs`、`ovl_`、`redirect_dir`、`metacopy`、`xino` 补充测试或工具仓库。
2. composefs 上游命名迁移：`containers/composefs` 与 `composefs/composefs` 当前指向同一 HEAD；manifest 采用 `composefs/composefs`，但验证脚本应允许重定向。
3. Nydus 仓库迁移：旧 `dragonflyoss/image-service` 已迁移到 `dragonflyoss/nydus`，不应收旧地址。
4. virtiofsd 实现迁移：老 QEMU 树内 C virtiofsd 与独立 Rust `virtio-fs/virtiofsd` 的关系需要标注。研究现代主线必须收独立 Rust 仓库，同时保留 QEMU block/virtio 上下文。
5. containerd snapshotter 路径变化：containerd v2 以后包路径可能调整，验证时不要只依赖固定目录名，应同时用符号搜索 `Snapshotter`, `overlay`, `mount`, `content.Store`。
6. CSI 边界膨胀：CSI 相关仓库很容易膨胀到几十个 sidecar 和云驱动。Agent 07 只保留直接体现文件/块存储实现的驱动，后续新增必须写明数据路径价值。
7. SPDK 子模块与第三方依赖：SPDK 有复杂 submodule/third_party 关系。源码计数应区分 SPDK 自身源码与 vendored DPDK/ISA-L 等依赖，避免重复计数。
8. QEMU submodule 和 generated code：QEMU 的 subprojects、ROM、generated trace/header 可能污染计数，需要排除构建目录和生成文件。
9. 懒加载镜像实现更新快：stargz、Nydus、SOCI、overlaybd 的活跃度和集成状态不同，应记录 HEAD 日期和默认分支，避免旧实验项目误判为主线。
10. 代码量估算偏差：不同工具对 protobuf、generated Go、Rust build artifacts、tests、vendored deps 的口径不同。最终只能以统一脚本计数为准。

## 验证方法

### 1. 远端与默认分支验证

对 manifest 中所有仓库执行：

```bash
while read -r name url; do
  head_ref=$(git ls-remote --symref "$url" HEAD 2>/dev/null | awk '/^ref:/ {print $2; exit}')
  if [ -n "$head_ref" ]; then
    printf "OK\t%s\t%s\t%s\n" "$name" "$head_ref" "$url"
  else
    printf "FAIL\t%s\t%s\n" "$name" "$url"
  fi
done < indexes/remotes-agent07.tsv
```

已在 2026-06-15 手动验证过本方案中的核心远端均可访问，默认分支包括 `master`、`main`、`devel`、`develop` 等，不要假设所有仓库都是 `main`。

### 2. 源码目录存在性验证

核心路径检查：

```bash
test -d src/00-kernel/linux/fs/overlayfs
test -d src/00-kernel/linux/fs/fuse
test -f src/00-kernel/linux/drivers/block/nbd.c
test -d src/05-virtio-qemu/qemu/block
test -d src/06-block-nbd-spdk/spdk/lib/bdev
test -d src/03-image-snapshotters/stargz-snapshotter
test -d src/03-image-snapshotters/nydus
test -d src/03-image-snapshotters/soci-snapshotter
test -d src/04-composefs-readonly/composefs
```

语义搜索检查：

```bash
rg -n "ovl_|overlayfs|metacopy|redirect_dir" src/00-kernel/linux/fs/overlayfs src/01-fuse-overlay
rg -n "Snapshotter|Prepare\\(|Commit\\(|Mounts\\(" src/02-container-storage src/03-image-snapshotters
rg -n "stargz|estargz|ztoc|rafs|nydus|composefs|fs-verity|verity" src/03-image-snapshotters src/04-composefs-readonly src/00-kernel
rg -n "virtiofs|vhost-user-fs|FUSE_INIT|FUSE_LOOKUP" src/05-virtio-qemu src/00-kernel/linux/fs/fuse
rg -n "nbd|bdev|blobfs|vhost|nvme" src/06-block-nbd-spdk
rg -n "NodePublishVolume|ControllerPublishVolume|mount" src/07-csi-direct
```

### 3. 源码行数验证

优先使用 `scc` 或 `tokei`；没有时用 `cloc`。统一排除：

- `.git`
- `vendor`, `third_party`, `node_modules`, `target`, `build`, `_build`, `dist`
- `docs`, `Documentation`, `man`, `website`
- `testdata`, `fixtures`
- 生成文件：`*.pb.go`, `*.generated.*`, `*.gen.*`, `bindata.go`

示例：

```bash
scc src \
  --exclude-dir .git,vendor,third_party,node_modules,target,build,_build,dist,docs,Documentation,man,website,testdata,fixtures \
  --exclude-ext md,rst,txt,png,jpg,jpeg,gif,svg,pdf \
  --format tabular > indexes/loc-agent07.tsv
```

验收门槛：

- `must` 集合源码行数大于 2000 万行。
- `must + optional` 源码行数小于 2 亿行。
- Linux、QEMU、SPDK 三个大仓库合计不应低于总源码行数的 70%，否则说明 clone 或计数口径可能有误。
- vendor/third_party 占比如果超过 15%，需要重新排除或单独列项。

### 4. 仓库去重和迁移验证

```bash
awk '{print $2}' indexes/remotes-agent07.tsv | sort | uniq -d
git -C src/04-composefs-readonly/composefs remote get-url origin
git -C src/03-image-snapshotters/nydus remote get-url origin
git -C src/05-virtio-qemu/virtiofsd remote get-url origin
```

重点确认：

- `composefs` 使用 `https://github.com/composefs/composefs.git`。
- `nydus` 使用 `https://github.com/dragonflyoss/nydus.git`，不是旧 `image-service` 地址。
- `virtiofsd` 使用 `https://gitlab.com/virtio-fs/virtiofsd.git`。
- `nbdkit` 和 `libnbd` 使用 GitLab 上游，不使用旧 GitHub 镜像。

### 5. 阅读入口验证

建议生成 `indexes/focus-paths-agent07.tsv`，每行包含：

```text
repo    tier    path    topic
```

最低应覆盖这些 topic：

- overlayfs-kernel
- fuse-overlayfs-rootless
- containerd-snapshotter-api
- containers-storage-overlay-driver
- stargz-lazy-pull
- nydus-rafs
- soci-ztoc
- composefs-verity
- virtiofs-kernel-and-daemon
- qemu-block-layer
- spdk-bdev-blob-vhost-nbd
- nbd-protocol-tools
- csi-node-publish-mount

