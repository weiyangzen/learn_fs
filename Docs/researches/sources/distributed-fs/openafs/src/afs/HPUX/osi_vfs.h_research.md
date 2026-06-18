# sources/distributed-fs/openafs/src/afs/HPUX/osi_vfs.h

## sources/distributed-fs/openafs/src/afs/HPUX/osi_vfs.h

Purpose: provides small HP-UX VFS compatibility definitions for OpenAFS.

Important APIs/types/functions: defines `LOCK_SH`, `LOCK_EX`, `LOCK_NB`, `LOCK_UN`, maps `d_fileno` to `d_ino`, and defines `splclock()` as `spl7()`.

Control flow: none.

State/persistence: none.

Dependencies/integration: used by HP-UX vnode and lock code that expects BSD-like flock constants and dirent field names.

Risks/test signals: constants must match HP-UX lockf/flock expectations. Test advisory lock translation and directory entry consumers.
