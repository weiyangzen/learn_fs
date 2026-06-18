# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metadir.h

Purpose: Declares the metadata directory tree update interface and `struct xfs_metadir_update`, the state object used to create or link internal metadata files.

Important APIs and types: `struct xfs_metadir_update` carries parent directory, path component, parent-pointer context, child inode, transaction, metadata file type, and lock-state bits. Declared operations cover load, start/create, start/link, commit/cancel, and mkdir.

Control flow: callers fill an update structure, call a start function to allocate resources and lock inodes, call create/link, then must call commit or cancel. The API intentionally separates resource acquisition from mutation so callers can finish setup of returned metadata inodes.

State and persistence: the structure tracks transient transaction and lock state around persistent metadir mutations. `metafile_type` becomes persistent inode metadata through `xfs_metafile_set_iflag`.

Dependencies and integration: consumed by quota/metafile/realtime metadata creation and repair paths. It depends on parent pointer declarations and metadata file type enums from core XFS format headers.

Risks and test signals: misuse can leak locks or transactions, especially because create can return an inode even on error. Tests should assert every start path is paired with commit/cancel and exercise cleanup of partially initialized metadata inodes.
