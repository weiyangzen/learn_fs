# sources/distributed-fs/ceph-client/fs/afs/xdr_fs.h

Purpose: Defines on-wire AFS fileserver XDR structures for fetch status and directory pages, plus constants used by directory parsing and layout code.

Important APIs and types: `struct afs_xdr_AFSFetchStatus` maps the AFS3 fetch-status record, including type, link count, 64-bit size/data-version split fields, access masks, mode, parent IDs, timestamps, group, lock count, and abort code. `union afs_xdr_dirent`, `struct afs_xdr_dir_hdr`, `union afs_xdr_dir_block`, and `struct afs_xdr_dir_page` describe the 2048-byte AFS directory block format. `afs_dir_calc_slots()` computes standardized directory-entry slot counts.

Control flow: This is a header-only contract. Consumers decode network-byte-order fields and use the directory constants to walk hash tables, allocation bitmaps, directory blocks, and page-sized groups of blocks.

State and persistence: The structures describe persisted server-side wire/directory data, not local runtime state. Packed layout is essential because these definitions map directly onto network or page-cache bytes.

Dependencies and integration points: Depends on kernel endian types and `PAGE_SIZE`. It is included by AFS/YFS client and directory code that must share exactly the same layout assumptions as servers.

Risks: Any layout change would break wire compatibility. `afs_dir_calc_slots()` intentionally uses the standardized historical 16-byte first-slot calculation even though the C structure name array is effectively larger; changing this would corrupt directory parsing.

Test signals: Decode status records with high size/data-version bits, parse directories spanning multiple 2048-byte blocks per page, verify slot counts for short and long names, and assert packed sizes against protocol expectations.
