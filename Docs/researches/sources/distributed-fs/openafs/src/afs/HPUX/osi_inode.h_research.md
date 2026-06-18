# sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.h

## sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.h

Purpose: defines HP-UX UFS inode metadata layout used by OpenAFS Vice inode operations.

Important APIs/types/functions: defines `BAD_IGET`, `VICEMAGIC`, `DI_VICEP3`, `I_VICE3`, UID extraction helpers, aliases for `i_vicemagic`, `i_vicep1..4`, `di_vicemagic`, `di_vicep1..4`, magic tests/clear macros, and the `igetinode` prototype.

Control flow: no runtime control flow; macro expansion maps OpenAFS fields onto HP-UX inode/dinode members.

State/persistence: persists AFS volume/vnode/uniquifier/data fields in inode spare, generation, flag, and UID msb/lsb fields. The comment explains `VICEMAGIC` is placed in `ic_flags` to interact with HP-UX large-UID handling.

Dependencies/integration: consumed by HP-UX inode and file cache code plus server/salvager paths that interpret Vice inodes.

Risks/test signals: field aliasing is architecture/compiler sensitive and can conflict with native UFS semantics. Test by creating Vice inodes, running salvager/list-inode tooling, verifying metadata survives reboot/fsck, and checking large UID behavior.
