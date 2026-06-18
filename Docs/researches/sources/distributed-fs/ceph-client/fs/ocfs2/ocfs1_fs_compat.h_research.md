# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs1_fs_compat.h

Purpose: defines OCFS1-compatible sector-0 and sector-1 volume structures that OCFS2 writes so older OCFS1 tooling recognizes the device and fails cleanly rather than mis-mounting it.

Important APIs and types: constants define OCFS1 signature, version, label, UUID, mount-point, and cluster-name lengths. `struct ocfs1_vol_disk_hdr` describes the sector-0 OCFS1 volume header. `struct ocfs1_disk_lock` mirrors the old disk lock shape with explicit padding. `struct ocfs1_vol_label` describes the sector-1 label containing disk-lock, label, volume ID, and cluster-name fields.

Control flow: this header contains no executable flow; formatting and compatibility code include it when laying out the first sectors of a new OCFS2 volume.

State and persistence: all structures are on-disk compatibility records. They are not the active OCFS2 superblock; OCFS2's real superblock starts at `OCFS2_SUPER_BLOCK_BLKNO` from `ocfs2_fs.h`.

Dependencies and integration: depends on fixed-width kernel integer types and is coupled to mkfs/tunefs behavior and any mount detection code that validates the OCFS1 signature.

Risks: field size, alignment, or signature changes can break the protective compatibility mechanism and confuse old tools. Because these structures live in fixed sectors, packing and padding assumptions are ABI-sensitive.

Test signals: mkfs image inspection of sectors 0 and 1, old OCFS1 mount rejection behavior, endian/layout checks, and compatibility tests that verify OCFS2 superblock discovery still starts at block 2.
