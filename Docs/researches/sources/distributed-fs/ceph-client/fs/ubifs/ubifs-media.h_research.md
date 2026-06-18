# sources/distributed-fs/ceph-client/fs/ubifs/ubifs-media.h

## Purpose

`sources/distributed-fs/ceph-client/fs/ubifs/ubifs-media.h` is the UBIFS on-flash format contract. It defines the magic/version values, minimum geometry constants, key and node type namespaces, compression and feature flags, and every packed media node layout that the rest of UBIFS reads from or writes to UBI logical eraseblocks. The source was read as a complete 855-line header.

## Important APIs, Types, and Functions

This header exports no functions; its API is the ABI itself. Important constants include `UBIFS_NODE_MAGIC`, `UBIFS_FORMAT_VERSION`, `UBIFS_RO_COMPAT_VERSION`, `UBIFS_BLOCK_SIZE`, `UBIFS_MAX_NLEN`, `UBIFS_MAX_KEY_LEN`, the fixed area LEB numbers (`UBIFS_SB_LNUM`, `UBIFS_MST_LNUM`, `UBIFS_LOG_LNUM`), node-size macros, hash/HMAC maxima, `UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT`, and flag masks such as `UBIFS_FLG_MASK`. Important enums cover LPT node types, inode file types, key hash/format/type values, inode flags, compression types, node types, master flags, node group states, and superblock flags. Packed media structs include `ubifs_ch`, `ubifs_ino_node`, `ubifs_dent_node`, `ubifs_data_node`, `ubifs_trun_node`, `ubifs_pad_node`, `ubifs_sb_node`, `ubifs_mst_node`, `ubifs_ref_node`, `ubifs_auth_node`, `ubifs_sig_node`, `ubifs_branch`, `ubifs_idx_node`, `ubifs_cs_node`, and `ubifs_orph_node`.

## Control Flow

There is no runtime control flow in this header. Runtime code uses these definitions when formatting nodes, validating scanned LEB data, replaying journal entries, building index branches, committing master/LPT/orphan state, and handling authenticated images. The common node header makes all node parsers start with magic, CRC, sequence number, length, type, and group fields before dispatching to the type-specific layout.

## State and Persistence Behavior

All defined structures are persistent little-endian media layouts. Superblock nodes persist filesystem geometry, feature flags, UUID, default compression, authentication material, and compatibility versions. Master nodes persist commit roots, log pointers, free/dirty/used/dead/dark accounting, LPT roots, GC state, and authentication hashes. Inode, dent/xent, data, truncation, ref, index, commit-start, orphan, auth, and signature nodes persist the logical filesystem tree and journal. Padding fields are part of the ABI and must remain zeroed by writer-side helpers.

## Dependencies and Integration Points

`ubifs.h` includes this header and layers in-memory state and function prototypes on top of it. The layouts integrate with UBIFS I/O validation, journal replay, TNC index management, LPT space accounting, xattr support, fscrypt, authentication, recovery, and mkfs/bootloader compatibility. The code relies on Linux fixed-width little-endian types and packed structs.

## Risks and Edge Cases

Changing field order, sizes, enum values, flags, or alignment breaks on-flash compatibility. Padding fields require matching zeroing helpers. Authenticated branch hashes are stored after variable-sized keys, so consumers must use `c->key_len` and `c->hash_len` rather than assuming a static struct size. Size macros and maxima must stay aligned with validation logic. Superblock flags and compatibility versions gate whether older kernels or bootloaders can safely mount an image.

## Test Signals

Useful signals include UBIFS mount/recovery tests across format versions, fsck-style node validation, CRC and authentication failure tests, mkfs image compatibility tests, xattr and encryption-context image tests, endian/layout checks for packed structs, and journal replay tests involving truncation, orphan, index, auth, and signature nodes.
