<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gfs2_ondisk.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gfs2_ondisk.h

## Purpose
`gfs2_ondisk.h` defines the stable on-disk format for GFS2 metadata. It is consumed by the kernel filesystem, recovery paths, and userspace tools that inspect, create, repair, or upgrade GFS2 volumes.

## Important APIs, types, and functions
Key constants include `GFS2_MAGIC`, basic block size, non-disk lock numbers, format numbers, metatype IDs, `GFS2_SB_ADDR`, resource-group bitmap states, resource-group flags, dinode flags, directory limits, EA type/flag values, log header flags, log flush caller bits, log descriptor types, and quota flags. Fixed layouts include `struct gfs2_inum`, `gfs2_meta_header`, `gfs2_sb`, `gfs2_rindex`, `gfs2_inode_lvb`, `gfs2_rgrp_lvb`, `gfs2_rgrp`, `gfs2_quota`, `gfs2_dinode`, `gfs2_dirent`, `gfs2_leaf`, `gfs2_ea_header`, `gfs2_log_header`, `gfs2_log_descriptor`, `gfs2_inum_range`, `gfs2_statfs_change`, `gfs2_quota_change`, and `gfs2_quota_lvb`.

## Control flow
There is no code flow in the header. Runtime consumers read blocks, validate `mh_magic`, `mh_type`, and format fields, convert big-endian fields to CPU order, then dispatch to resource group, dinode, directory, extended attribute, log, statfs, quota, or lock-value-block handling. Journal recovery interprets log headers and descriptors before replaying or revoking metadata.

## State and persistence behavior
Almost every structure here is persistent disk or distributed-lock state. The ABI preserves historical padding for GFS1 compatibility, old superblock upgrades, and fixed journal formats. Resource group bitmaps persist allocation state, dinodes persist file metadata, log records persist recovery state, and LVBs mirror cluster-visible lock state.

## Dependencies and integration points
It depends on `<linux/types.h>` and POSIX mode bits used by `DT2IF()`/`IF2DT()`. It integrates with gfs2 kernel code, dlm lock state, gfs2-utils, fsck, mkfs, quota tooling, NFS generation handling, and journal recovery.

## Risks and test signals
Risks include endian mistakes, changing reserved fields, incorrect directory record alignment, resource bitmap state corruption, CRC/hash mismatches, log version confusion around `LH_V1_SIZE`, and cross-node compatibility breaks. Test signals are mkfs/fsck round trips, endian sparse checks, mount/recovery tests after forced shutdown, resource group allocation tests, xattr boundary tests, quota updates, statfs local/global reconciliation, and old-format volume compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gfs2_ondisk.h -->
