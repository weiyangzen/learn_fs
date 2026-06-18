# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_leaf.h

## Purpose
`xfs_attr_leaf.h` declares the in-core attribute leaf header and the shortform/leaf/node helper API exported by `xfs_attr_leaf.c` to the rest of XFS. It is the interface boundary for manipulating leaf blocks, converting formats, and checking attr leaf buffer validity.

## Important APIs, types, and functions
The central type is `struct xfs_attr3_icleaf_hdr`, containing sibling links, magic, entry count, used bytes, 32-bit `firstused`, holes flag, and three freemap entries. The 32-bit `firstused` is an explicit abstraction over the 16-bit on-disk field.

Shortform declarations include creation, replacement, add, getvalue, conversion to leaf, removal, find-name, all-fit, bytes-fit, verifier, and fork removal APIs. Leaf/node declarations include conversion to node/shortform, incomplete flag operations, split, lookup, getvalue, add, remove, list, init, toosmall, unbalance, last hash, ordering, new entry sizing, leaf read, header conversion, and owner/header checking.

## Control flow
Callers in `xfs_attr.c` use these prototypes to dispatch by attr fork format. Da-btree code uses split, toosmall, unbalance, order, and last-hash helpers to maintain tree shape. Lookup and getvalue are leaf-buffer-local helpers used both by single-leaf and node-leaf paths. Conversion APIs move persistent data among inode-local shortform, block leaf, and da-node structures.

## State and persistence behavior
The header formalizes the incore state used to safely edit and log leaf blocks. `firstused`, `usedbytes`, `holes`, and `freemap[]` must match the packed on-disk leaf layout. Incomplete flag APIs are part of the persistence protocol for remote values and replace atomicity. Read and header-check APIs tie leaf buffers to verifiers and owners, particularly for CRC-enabled filesystems.

## Dependencies and integration points
The header forward-declares `xfs_da_args`, `xfs_da_state`, `xfs_da_state_blk`, `xfs_inode`, `xfs_trans`, and attr-list context to avoid heavy includes. It assumes format definitions for attr leaf map size and on-disk structures are already available from XFS format headers. It is consumed by the attr core, list handling, da-btree code, repair/recovery paths, and any code that initializes attr leaf buffers.

## Risks and edge cases
Changing `struct xfs_attr3_icleaf_hdr` semantics can silently break endian conversion and verifier assumptions. The API exposes low-level operations that require callers to hold the right transaction, inode locks, owner, geometry, and fork context. `xfs_attr3_leaf_list_int` is declared here but implemented in sibling list code, so linkage assumptions matter. `xfs_attr_leaf_newentsize` decides local versus remote storage by side effect through its `local` out parameter; callers must pass it consistently with reservation and remote allocation code.

## Test signals
Compile and link tests should ensure all declarations match implementation signatures. Functional tests should exercise every exported conversion and flag operation through higher-level xattr operations, plus direct verifier tests for malformed leaf headers, freemaps, and owner mismatches. Static checks should flag callers that invoke leaf APIs without transaction or attr geometry initialization.
