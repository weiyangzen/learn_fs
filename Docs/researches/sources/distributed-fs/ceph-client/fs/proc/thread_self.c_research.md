<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/thread_self.c -->
## sources/distributed-fs/ceph-client/fs/proc/thread_self.c

Purpose: implements the persistent `/proc/thread-self` symlink, resolving to the caller's task directory path within its thread group.

Important APIs and functions: `proc_thread_self_get_link`, `proc_setup_thread_self`, `proc_thread_self_init`, and global `thread_self_inum`.

Control flow: init allocates a stable inode number. Superblock fill creates a persistent symlink dentry named `thread-self`. Link resolution computes both TGID and TID in the proc mount's PID namespace and formats `"<tgid>/task/<pid>"` into a delayed-call-freed buffer.

State and persistence behavior: the dentry/inode are persistent per proc superblock, while the target string is dynamically generated per caller. The inode number is allocated once at boot.

Dependencies and integration points: depends on proc superblock PID namespace state, scheduler PID/TGID namespace helpers, proc root setup, and VFS symlink delayed calls.

Risks: returns `-ENOENT` if the caller lacks a PID in the mount namespace. RCU path walk requires atomic allocation or `-ECHILD`. The target format is ABI-stable and must match `/proc/<tgid>/task/<tid>`.

Test signals: readlink from main thread and secondary threads; nested PID namespace behavior; RCU lookup path; compare target with `/proc/self/task/<tid>` existence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/thread_self.c -->
