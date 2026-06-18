<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/inode.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/inode.c

Purpose: Implements inode-core scrub: acquiring the target inode safely, validating on-disk inode fields via an incore copy, and cross-referencing inode allocation and fork counters with other metadata.

Important APIs, types, and functions: Exports `xchk_setup_inode()` and `xchk_inode()`. Important helpers include `xchk_prepare_iscrub()`, `xchk_install_handle_iscrub()`, `xchk_dinode()`, `xchk_inode_flags()`, `xchk_inode_flags2()`, `xchk_inode_extsize()`, `xchk_inode_cowextsize()`, `xchk_inode_xref_finobt()`, `xchk_inode_xref_bmap()`, `xchk_inode_xref()`, `xchk_inode_check_reflink_iflag()`, and `xchk_inode_check_unlinked()`.

Control flow: Setup handles the open file, handle-based lookup, metadata-directory restrictions, invalid inode numbers, safe untrusted iget, and fallback AGI-protected imap lookup when iget fails due to corruption. If repair is possible and the inode cannot be instantiated, setup saves the raw imap for inode repair. Scrub copies the incore inode to a disk-format dinode, validates mode, version, metatype, ids, format, timestamps, size, block counts, flags, fork offsets, attr/data formats, extent counters, extsize hints, and feature compatibility. If the core is clean, regular files get reflink-iflag verification, all inodes get unlinked-list consistency checks, and xrefs check used space, finobt state, rmap ownership, sharing/COW staging, and fork block counts.

State and persistence: Scrub itself does not persist changes. It may keep a transaction and AGI buffer in setup to preserve the evidence needed by repair when an allocated inode cannot be loaded. Findings are recorded in scrub output flags and inode-specific corrupt/warning/preen state.

Dependencies and integration points: Depends on VFS inode locking, XFS iget/imap, quota attach, transactions, inode buffer/fork validators, reflink, rmap/refcount xrefs, finobt, bmap extent counting, metadata directory policy, and `inode_repair.c` for raw-inode salvage.

Risks and test signals: Acquisition fallback is delicate because setup must distinguish free inodes, corrupt inobt, and allocated-but-unloadable inodes. Validation risks include feature-gated flags, realtime/reflink interactions, attr fork boundary math, and block count comparisons for shared extents. Test open-file and handle scrub, bad inode numbers, corrupt dinodes that fail iget, v1/v2/v3 inode fields, metadir inodes, realtime and reflink files, large extent counts, invalid timestamps, unlinked-list mismatches, finobt disagreement, and xref degradation when secondary btrees are sick.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/inode.c -->
