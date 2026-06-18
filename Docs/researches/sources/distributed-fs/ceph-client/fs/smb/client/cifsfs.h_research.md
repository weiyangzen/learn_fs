# sources/distributed-fs/ceph-client/fs/smb/client/cifsfs.h

Purpose: declares the CIFS VFS-facing interface exported across the SMB client. It names the filesystem types, inode/file/address-space/dentry operation tables, mount entry point, inode and dentry helpers, and user-visible version constants.

Important APIs and types: defines `ROOT_I`, `SMB3_PRODUCT_BUILD`, `CIFS_VERSION`, temporary/silly rename name prefixes, `cifs_uniqueid_to_ino_t`, `cifs_set_time`, and `cifs_get_time`. It declares `cifs_fs_type`, `smb3_fs_type`, inode operations, file operations, dentry operations, address-space operations, root inode lookup, create/open/lookup/unlink/link/mkdir/rmdir/rename/revalidation/getattr/setattr/fiemap helpers, file read/write/lock/fsync/flush/mmap/readdir helpers, `cifs_file_copychunk_range`, `cifs_ioctl`, `cifs_setsize`, and `cifs_smb3_do_mount`.

Control flow: the header has no runtime flow, but it defines the cross-file call graph between `cifsfs.c`, inode/namei/file/dir/xattr/export modules, and VFS registration. Inline inode conversion hashes 64-bit server file ids down for 32-bit `ino_t` while avoiding inode number zero. Dentry time helpers store attribute-cache timestamps in `d_fsdata`.

State and persistence behavior: persistent state is not stored here. The declared APIs manipulate VFS inode/dentry/pagecache state, server file ids, temporary delete-on-close names, mount roots, and remote file state through implementations elsewhere. The version constants identify the client module version exposed at module metadata level.

Dependencies and integration points: includes Linux hash and dcache APIs and is included by files implementing CIFS VFS operations. It also exposes optional xattr and NFSD export hooks behind config guards.

Risks: `cifs_uniqueid_to_ino_t` intentionally hashes server ids on 32-bit architectures, so inode collisions remain possible and must be handled by inode lookup code. Storing timestamps in `d_fsdata` assumes no other dentry subsystem consumer overwrites it. Prototype drift here can break operation table wiring or optional config builds.

Test signals: 32-bit inode-number behavior with large server ids, attribute-cache timeout behavior through dentry timestamp helpers, builds with and without xattr/NFSD export support, VFS operation table linkage, and module version consistency when changed.
