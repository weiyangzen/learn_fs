# sources/distributed-fs/ceph-client/fs/smb/client/smb1misc.c

## Purpose
`smb1misc.c` contains SMB1 header assembly, oplock-break/change-notify recognition, and SMB message size calculation.

## Important APIs, types, and functions
The exported functions are `header_assemble`, `is_valid_oplock_break`, and `smbCalcSize`. `header_assemble` initializes an SMB1 header and base request length. `is_valid_oplock_break` parses unsolicited/async SMB1 notifications. `smbCalcSize` computes length from header, word count, and byte count.

## Control flow
Header assembly zeroes a small header area, writes `0xFFSMB`, command, flags, pid, tree/session identifiers, unicode/status/DFS/case/signing flags, MID, and word count. Oplock handling first recognizes NT transact change notify responses, including data-offset validation. It then handles `SMB_COM_LOCKING_ANDX` oplock-release requests, ignores expected invalid-handle/bad-fid responses, finds the matching session/tree/open file by TID and FID, marks the inode for oplock break, updates file oplock fields, and queues break handling.

## State and persistence
The file mutates outgoing SMB headers and runtime inode/open-file state for oplock breaks. It increments tree statistics and sets `CIFS_INODE_PENDING_OPLOCK_BREAK`. No disk state is written.

## Dependencies and integration points
It depends on SMB1 PDU layouts, global CIFS session and tcon lists, open-file lists, inode private state, statistics counters, and oplock worker queuing. `smb1ops.c` exposes these helpers through the dialect operation table.

## Risks and test signals
Risks include malformed notify offsets, races while scanning sessions and open files, stale oplock breaks after close, incorrect MID/TID/UID fields on assembled requests, and byte-count based size errors. Test signals include header assembly with/without tcon/session/server signing, DFS shares, unicode and non-unicode sessions, valid and invalid change notify responses, oplock breaks for open and recently closed files, and `smbCalcSize` on varying word/byte counts.
