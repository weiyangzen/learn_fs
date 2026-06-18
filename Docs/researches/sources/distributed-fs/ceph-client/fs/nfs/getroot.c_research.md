# sources/distributed-fs/ceph-client/fs/nfs/getroot.c

Purpose: obtains the root inode and dentry for an NFS mount after the superblock and mount context have been prepared.

Important APIs and functions: `nfs_get_root` is the external entry point. `nfs_superblock_set_dummy_root` installs an invisible dummy root dentry on the superblock. It also uses `nfs_alloc_fattr_with_label`, protocol `getroot`, `nfs_fhget`, `d_obtain_root`, `security_sb_set_mnt_opts`, `security_sb_clone_mnt_opts`, and `nfs_setsecurity`.

Control flow: `nfs_get_root` duplicates the mount source for dentry private data, allocates root fattrs, asks the protocol ops to getattr the mount root filehandle, converts the filehandle/fattrs to an inode, ensures the superblock has a dummy root, obtains the actual root dentry, attaches the source name to anonymous root dentries, applies or clones LSM mount options, adjusts the security-label capability if LSMs did not accept native labels, sets inode security from fattrs, and returns the root in `fc->root`.

State and persistence behavior: `sb->s_root` may be initialized once to a dummy dentry whose alias is removed from the inode alias list so later dentry splicing does not expose it incorrectly. `fc->root` receives a referenced root dentry. `root->d_fsdata` may own the duplicated source string. Server `has_sec_mnt_opts` and `NFS_CAP_SECURITY_LABEL` can be updated based on security setup.

Dependencies and integration points: integrates mount context state from `fs_context.c`, server/protocol operations, inode construction in `inode.c`, VFS dentry/root helpers, and Linux security hooks. Clone mounts use the parent superblock security options and require the cloned root to be a directory.

Risks: error unwinding must free fattrs/source strings and drop `fc->root` when security setup fails. The dummy root alias manipulation is subtle but protects unmount/shrinker assumptions. Security-label capability is modified based on LSM output flags, so mount behavior can differ by active LSM configuration. Clone data with a non-directory root returns `-ESTALE`.

Test signals: successful NFS root mount, failed protocol getroot, inode creation failure, dentry allocation failure, clone mount from a parent superblock, LSM context and native-label mounts, non-directory clone roots, and dentry alias/shrinker behavior during unmount.
