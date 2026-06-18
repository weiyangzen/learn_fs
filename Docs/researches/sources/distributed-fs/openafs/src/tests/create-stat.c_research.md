<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-stat.c -->
# sources/distributed-fs/openafs/src/tests/create-stat.c

## Purpose
Validates that creating a sibling file does not perturb an existing AFS file's inode identity and that the POSIX inode matches the VenusFid-derived AFS file id.

## Important APIs, Types, and Functions
functions: usage, main; AFS calls/macros: fs_lib, fs_getfid

## Control Flow
Requires one filename, opens the original, creates `<file>.new` with O_EXCL, compares stat/lstat inode values before and after creation, calls `fs_getfid`, computes the expected AFS inode from Volume/Vnode, then unlinks both files.

## State and Persistence Behavior
Creates and removes the supplied file and a `.new` sibling; errors attempt cleanup before failing.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces fs_lib, fs_getfid

## Risks and Test Signals
Strongly AFS-specific because it depends on `pioctl(VIOCGETFID)` semantics and the inode derivation formula; failures signal vnode identity regression or stale stat metadata.

## Source Notes
Read as C program; 145 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-stat.c -->
