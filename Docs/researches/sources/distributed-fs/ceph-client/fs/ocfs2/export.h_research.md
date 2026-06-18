# sources/distributed-fs/ceph-client/fs/ocfs2/export.h

Purpose: declares the OCFS2 NFS/exportfs operation table.

Important APIs and types: includes `<linux/exportfs.h>` and exposes `extern const struct export_operations ocfs2_export_ops`.

Control flow: none in the header. It provides the symbol that superblock setup can reference to enable NFS export support.

State and persistence behavior: none directly; state is handled by `export.c` through encoded file handles and OCFS2 inode generation/block numbers.

Dependencies and integration points: used by OCFS2 superblock/export setup code and implemented by `export.c`. It connects OCFS2 to the generic Linux exportfs/NFS server infrastructure.

Risks: the header is intentionally narrow. The main compatibility risk is that any change to `ocfs2_export_ops` consumers must keep this declaration synchronized.

Test signals: build coverage with exportfs/NFS server support and mounting an exported OCFS2 volume.
