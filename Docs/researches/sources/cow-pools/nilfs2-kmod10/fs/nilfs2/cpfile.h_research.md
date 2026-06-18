# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/cpfile.h

Public interface for checkpoint file operations. It declares checkpoint read/create/finalize/delete APIs, checkpoint mode changes, snapshot checks, checkpoint stats, cpinfo enumeration, and cpfile inode loading.

Integration: consumed by mount/recovery/root management and ifile initialization. It exposes cpfile behavior through kernel NILFS API structures such as `nilfs_cpstat`, `nilfs_cpinfo`, and on-disk checkpoint structures.

Risk/notes: callers must distinguish checkpoint numbers from current metadata cno boundaries; several operations reject cno 0 or future checkpoint numbers.
