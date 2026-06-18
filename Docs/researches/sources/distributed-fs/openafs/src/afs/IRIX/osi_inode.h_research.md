# sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.h

## sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.h

Purpose: defines IRIX inode metadata constants and layout notes for AFS server/salvager support.

Important APIs/types/functions: defines `BAD_IGET`, `XFS_VICEMAGIC`, `DI_VICEP3`, `I_VICE3`, masks for SGI inode fields, `struct afsparms`, and `dmag` for disk inode extent magic access.

Control flow: none; this is a macro/type header.

State/persistence: documents two metadata schemes: XFS uses `XFS_VICEMAGIC`; older EFS-style inodes use unused `ex_magic` fields plus `di_version` to encode volume, vnode, uniquifier, data version, and special inode metadata.

Dependencies/integration: used by `osi_inode.c` and any IRIX salvager/fileserver code interpreting Vice inode parameters.

Risks/test signals: on-disk field packing is filesystem-version sensitive. Test list/create/increment/decrement tooling across XFS and any legacy EFS expectations, and verify masks do not truncate required volume/vnode data unexpectedly.
