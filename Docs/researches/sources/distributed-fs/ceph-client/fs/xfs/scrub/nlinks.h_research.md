# sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks.h

## Purpose
`nlinks.h` defines the shared in-core data model for live link-count scrub and repair. It is the contract between `nlinks.c` and `nlinks_repair.c`.

## Important APIs, Types, And Functions
`struct xchk_nlink_ctrs` owns the scrub context, shadow `xfarray`, mutex, collection and comparison iscans, directory update hook, orphanage adoption request, and reusable name buffer. `struct xchk_nlink` stores observed parent links, child-directory backreferences, child forward links/dot entries, and record flags.

Flags are `XCHK_NLINK_WRITTEN`, `XCHK_NLINK_COMPARE_SCANNED`, and `XREP_NLINK_DIRTY`. `xchk_nlink_total` computes the effective VFS link count from observed parent links plus directory dot accounting plus child forward links.

## Control Flow
The header has no standalone control flow. Its structures are initialized by setup in `nlinks.c`, filled during filesystem scans and live hook callbacks, read during comparison, and reused by repair to update inode core state and unlinked-list membership.

## State And Persistence Behavior
All state is volatile scrub state. `xchk_nlink_total` deliberately uses a 64-bit accumulator so callers can detect values above XFS link-count limits before updating or reporting corruption.

## Dependencies And Integration Points
It depends on `struct xfs_scrub`, `xfarray`, `xchk_iscan`, `xfs_dir_hook`, and orphanage adoption types. Repair depends on this header for the exact counter semantics; changing the meaning of `parents`, `backrefs`, or `children` would affect both detection and repair.

## Risks And Edge Cases
The subtle behavior is directory accounting: a linked directory contributes one dot link in `xchk_nlink_total`, while `children` tracks forward links from the directory to children and dot-style accounting. Root and metadata-root behavior is handled by callers, not the helper.

## Test Signals
Tests should confirm that directory, non-directory, unlinked directory, root directory, and overflow cases all produce expected totals.
