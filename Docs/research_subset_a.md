# Research Subset A: OS/VFS, Local Filesystems, COW Pools, Block Storage, and Virtualization

## Scope

This subset covers the `learn_fs` source trees centered on kernel and OS VFS implementations, public Windows filesystem implementations, teaching filesystem kernels, local filesystem tools and drivers, COW filesystem/pool implementations, block/storage substrate, and virtualization/block-device integration.

Code-only line budget: `15,256,852` focus-path lines across `58` default-counted source trees.

Complete source-tree coverage in this subset: `72` source trees.

## Deduplication

No source tree is deduplicated out of this two-way `learn_fs` split. The subset A and subset B plans together cover every row in `manifests/sources.tsv` exactly once.

Line budgets use `scripts/source_inventory.py --tier all --target-set default-count --scope focus-paths`; source trees with `default_count=no` remain included for research planning even when they do not contribute to the budget total.

## Included Source Trees

- `sources/os/linux/linux`
- `sources/os/linux/linux-stable`
- `sources/os/bsd/freebsd-src`
- `sources/os/bsd/openbsd-src`
- `sources/os/bsd/netbsd-src`
- `sources/os/bsd/dragonflybsd`
- `sources/os/illumos/illumos-gate`
- `sources/os/plan9/plan9`
- `sources/os/plan9/9front`
- `sources/windows/reactos`
- `sources/windows/windows-driver-samples`
- `sources/windows/winfsp`
- `sources/windows/dokany`
- `sources/windows/winbtrfs`
- `sources/teaching/xv6-riscv`
- `sources/teaching/xv6-public`
- `sources/teaching/minix`
- `sources/teaching/os161`
- `sources/teaching/pintos`
- `sources/local-fs/e2fsprogs`
- `sources/local-fs/xfsprogs`
- `sources/local-fs/xfsdump`
- `sources/local-fs/btrfs-progs`
- `sources/local-fs/btrfs-linux`
- `sources/local-fs/kdave-linux`
- `sources/local-fs/f2fs-tools`
- `sources/local-fs/erofs-utils`
- `sources/local-fs/dosfstools`
- `sources/local-fs/exfatprogs`
- `sources/local-fs/ntfs-3g`
- `sources/local-fs/udftools`
- `sources/local-fs/jfsutils`
- `sources/local-fs/reiserfsprogs`
- `sources/local-fs/squashfs-tools`
- `sources/local-fs/apfs-fuse`
- `sources/local-fs/linux-apfs-rw`
- `sources/cow-pools/openzfs`
- `sources/cow-pools/bcachefs`
- `sources/cow-pools/bcachefs-tools`
- `sources/cow-pools/nilfs-utils`
- `sources/cow-pools/nilfs2-kmod10`
- `sources/block-storage/bcache-tools`
- `sources/block-storage/util-linux`
- `sources/block-storage/mdadm`
- `sources/block-storage/parted`
- `sources/block-storage/linux-dm`
- `sources/block-storage/lvm2`
- `sources/block-storage/thin-provisioning-tools`
- `sources/block-storage/cryptsetup`
- `sources/block-storage/vdo`
- `sources/block-storage/kvdo`
- `sources/block-storage/stratisd`
- `sources/block-storage/stratis-cli`
- `sources/block-storage/devicemapper-rs`
- `sources/block-storage/libcryptsetup-rs`
- `sources/block-storage/libblkid-rs`
- `sources/virtualization/qemu`
- `sources/virtualization/virtiofsd`
- `sources/virtualization/spdk`
- `sources/virtualization/nbd`
- `sources/virtualization/nbdkit`
- `sources/virtualization/libnbd`
- `sources/virtualization/open-iscsi`
- `sources/virtualization/libguestfs`
- `sources/virtualization/guestfs-tools`
- `sources/virtualization/libblockdev`
- `sources/virtualization/nvme-cli`
- `sources/local-fs/mtd-utils`
- `sources/os/darwin/xnu`
- `sources/local-fs/ocfs2-tools`
- `sources/local-fs/gfs2-utils`
- `sources/local-fs/dlm`

## Why This Group

This subset is the filesystem foundation lane. It keeps VFS/vnode/page-cache implementations, local filesystem metadata and repair tooling, filesystem-oriented teaching kernels, Windows public filesystem stacks, COW pool/filesystem implementations, block-layer tools, and virtual block/device integration together.

The full default-counted `learn_fs` focus-path corpus is about `29,576,995` code-like lines. A two-way split targets about `14,788,498` lines per subset; this subset is about `15,256,852` lines.

## Research Cron Notes

- Use the `research-cron-builder` code-only scope.
- Preserve source-tree-aligned final artifacts under `Docs/researches/<source_path>_research.md`.
- Keep grouped prompts at or below `262144` bytes unless the final runner explicitly changes `GROUP_LIMIT_BYTES`.
- Chunk oversized files instead of sampling them.
- Do not mark the subset complete until per-file and folder-level indexes are OK.
