# sources/distributed-fs/ceph-client/fs/xfs/xfs_filestream.c

## Purpose
`xfs_filestream.c` implements directory-to-allocation-group associations for filestream allocation. It tries to keep files created under the same directory in a chosen AG to improve streaming layout while avoiding AGs preferred for metadata unless space is tight.

## Important APIs, types, and functions
The main public functions are `xfs_filestream_select_ag`, `xfs_filestream_deassociate`, `xfs_filestream_mount`, and `xfs_filestream_unmount`. Private `struct xfs_fstrm_item` stores an MRU-cache element and referenced `struct xfs_perag`. Key helpers are `xfs_filestream_pick_ag`, `xfs_filestream_get_parent`, `xfs_filestream_lookup_association`, and `xfs_filestream_create_association`.

## Control flow
Allocation calls `xfs_filestream_select_ag`, which resolves the parent inode from a dentry alias, looks for an MRU association keyed by parent inode, and reuses it if the AG has enough longest free extent or the transaction is in low-space mode. If lookup fails or is unsuitable, creation removes an old association, chooses a start AG from the old AG or inode32 rotor, adjusts adjacent allocation hints, scans AGs for an unused and sufficiently free candidate, and inserts a new MRU entry. The picker tracks a fallback AG with the most free blocks, performs a second pass for skipped AGF locks, then a low-space pass, and finally may share the fullest AG if no unassociated AG is available.

## State and persistence
All filestream associations are runtime MRU-cache state under `mp->m_filestream`. Each association holds a perag active reference and increments `pagf_fstrms`; expiry or deletion decrements and releases the AG. No on-disk metadata records the association.

## Dependencies and integration points
It integrates with XFS bmap allocation arguments, perag reference counting, AG reservation/free-space queries, MRU cache infrastructure, inode32 AG rotor tuning, directory parent lookup through dentries, tracepoints, and the mount/unmount lifecycle.

## Risks and test signals
Risks include stale or missing parent aliases, AG reference leaks, contention around `pagf_fstrms`, overuse of metadata-preferred AGs, poor fallback behavior under low space, and MRU expiry races. Test signals include creating many files in one directory, deleting/renaming directories, inode32 rotor behavior, AGF lock contention returning `-EAGAIN`, low-space transactions, metadata-preferred AG filtering, mount/unmount cache teardown, and filestream deassociation during inode inactivation.
