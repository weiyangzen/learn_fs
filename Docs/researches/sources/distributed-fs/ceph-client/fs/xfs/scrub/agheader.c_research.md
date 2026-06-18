# sources/distributed-fs/ceph-client/fs/xfs/scrub/agheader.c

## Purpose
This file implements online scrub validation for XFS allocation group headers: secondary superblocks, AGF, AGFL, and AGI. It verifies on-disk header geometry against the mounted primary superblock, checks per-AG counter consistency, validates btree roots and levels, and cross-references header blocks and AGFL entries against free-space, inode, rmap, refcount, shared, and CoW-staging metadata.

## Important APIs, types, and functions
`xchk_setup_agheader` prepares filesystem-level scrub and enables intent draining when required. `xchk_superblock` reads secondary superblocks with `xfs_sb_read_secondary`, compares fixed mkfs geometry as corruption and mutable propagated fields as preen candidates, and uses `xchk_superblock_ondisk_size` to ensure trailing bytes are zero for the active feature set. `xchk_agf`, `xchk_agfl`, and `xchk_agi` are the public scrub entry points for AGF, AGFL, and AGI. Helper cross-reference functions include `xchk_superblock_xref`, `xchk_agf_xref_*`, `xchk_agfl_xref`, `xchk_agfl_block_xref`, and `xchk_agi_xref_*`. `struct xchk_agfl_info` tracks expected AGFL count, discovered entries, uniqueness array, and buffers.

## Control flow and state
Header scrub normally reads the target AG headers through `xchk_ag_read_headers` or specific read helpers, rechecks verifiers with `xchk_buffer_recheck`, validates scalar fields, and only then performs cross-reference checks if the main corruption flag is still clear. AGF validation checks length, bnobt/cntbt/rmapbt/refcountbt roots and levels, AGFL circular counters, and in-core `pagf_*` counters. AGFL validation reads AGF and AGFL, walks active AGFL entries, records them into a temporary array, verifies count, sorts, and detects duplicates. AGI validation checks length, inobt/finobt roots and levels, inode counters, newino/dirino, unlinked buckets, padding, in-core `pagi_*` counters, and the in-memory iunlink chain.

## Persistence and integration
The file is read-only validation except for scrub state flags. It depends on mounted primary superblock data, perag state, buffer verifiers, btree cursors, and xref helpers from scrub common code. It integrates with online repair by setting corrupt or preen flags that later repair code consumes, and with health tracking through scrub result flags.

## Risks and test signals
Key risks are feature-gated superblock field comparisons, circular AGFL counter math, races with AG teardown, and xref checks that must degrade cleanly if btree cursors cannot be trusted. Useful tests include corrupt secondary superblock variants, stale mutable secondary superblock fields, invalid AGF roots/levels, inconsistent AGF counters versus btrees and perag state, duplicate or out-of-range AGFL entries, broken AGI unlinked bucket chains, and xref failure injection for missing btree cursors.
