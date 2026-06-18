<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_p.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_p.h

Purpose: defines Linux MD RAID persistent superblock formats, disk roles/states, feature bits, and helper macros used by mdadm and the kernel.

Important APIs and types: constants define reserved sectors, superblock sizes/word offsets, disk state bits, special disk roles, superblock magic, state bits, and feature-map bits. `mdp_disk_t` and `mdp_super_t` describe legacy 0.90 superblocks with endian-dependent event fields; `md_event()` reconstructs 64-bit event counters. `struct mdp_superblock_1` describes v1 little-endian superblocks, including array UUID/name, layout/chunk, reshape fields, offsets, device flags, bad-block log fields, event/resync state, and flexible `dev_roles[]`.

Control flow: mdadm and kernel MD code read component-device superblocks, validate magic/checksum/features, assemble arrays, select roles, track events, perform recovery/reshape, and write updated superblocks after state changes.

State and persistence: these structures are persistent on-disk RAID metadata. They encode array identity, geometry, events, resync/reshape checkpoints, per-device roles, bad block logs, write-intent bitmap/PPL/journal features, and clustered state.

Dependencies and integration points: depends on Linux endian/fixed types and host byte order for legacy layout. Integrates with MD RAID personalities, mdadm, boot auto-assembly, clustered MD, write-intent bitmaps, RAID reshape/recovery, and block-device metadata scanners.

Risks and test signals: high-risk areas are endian-specific legacy event fields, feature-bit compatibility, checksum coverage, flexible array sizing, reshape/backward/new-offset semantics, and data-loss from wrong roles. Test mdadm create/assemble/incremental, v0.90/v1.x superblocks, big-endian builds, reshape/recovery checkpoints, bad-block logs, PPL/journal features, clustered arrays, and corrupted metadata rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_p.h -->
