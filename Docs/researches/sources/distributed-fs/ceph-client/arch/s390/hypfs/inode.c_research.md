<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/inode.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/inode.c

Purpose: Implements the s390 hypervisor filesystem `s390_hypfs`, a single-instance pseudo filesystem exposing VM or LPAR hypervisor data and a writable `update` trigger.

Important APIs/types/functions: `hypfs_sb_info`, mount option parsing for `uid` and `gid`, inode/dentry creation helpers, `hypfs_read_iter()`, `hypfs_write_iter()`, `hypfs_create_u64()`, `hypfs_create_str()`, and filesystem registration through `__hypfs_fs_init()`. Source-visible declarations include: #define pr_fmt(fmt) "hypfs: " fmt; #define HYPFS_MAGIC 0x687970 /* ASCII 'hyp' */; #define TMP_SIZE 64 /* size of temporary buffers */; struct hypfs_sb_info {; struct dentry *update_file; /* file to trigger update */; struct mutex lock; /* lock to protect update process */; struct hypfs_sb_info *sb_info = sb->s_fs_info;; struct inode *inode = d_inode(sb_info->update_file);; struct dentry *next_dentry = hypfs_last_dentry->d_fsdata;; struct inode *ret = new_inode(sb);.

Control flow: Mount setup creates the root, asks the VM or DIAG backend to populate files, creates `update`, and records a monotonic timestamp. Regular file open snapshots `i_private` data under the superblock mutex. Writes to `update` are rate limited to one per second, delete the tracked top-level generated tree, repopulate from backend data, and advance the timestamp.

State and persistence behavior: Persistent state is per-superblock uid/gid, last-update time, update dentry, and generated inode `i_private` strings; `hypfs_last_dentry` globally tracks top-level generated dentries for update removal.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/errno.h>, #include <linux/fs.h>, #include <linux/fs_context.h>, #include <linux/fs_parser.h>, #include <linux/namei.h>, #include <linux/vfs.h>, #include <linux/slab.h>. Integrated with The file integrates VFS/fs_context/simplefs helpers, sysfs mount-point creation below `hypervisor_kobj`, s390 VM detection, EBCDIC conversion, and backend helpers from `hypfs.h`..

Risks: The global deletion list is not per-superblock even though the filesystem type uses `get_tree_single`; changing mount semantics would make this unsafe. Update repopulation is expensive and can race readers unless callers use the timestamp protocol.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 448 lines, 10904 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/inode.c -->
