# sources/distributed-fs/ceph-client/fs/ocfs2/filecheck.c

Purpose: implements OCFS2 online file checking through a per-volume sysfs directory. Users can request inode checks, inode fixes, and queue-size changes, then read back recent check/fix results.

Important APIs and functions: public lifecycle functions are `ocfs2_filecheck_create_sysfs` and `ocfs2_filecheck_remove_sysfs`. Internal types include `struct ocfs2_filecheck_entry` and `struct ocfs2_filecheck_args`. Main helpers are `ocfs2_filecheck_attr_show`, `ocfs2_filecheck_attr_store`, `ocfs2_filecheck_adjust_max`, `ocfs2_filecheck_args_parse`, `ocfs2_filecheck_handle`, `ocfs2_filecheck_handle_entry`, and queue erasure/done helpers.

Control flow: mount setup allocates `struct ocfs2_filecheck`, initializes the list/spinlock/default maximum, and creates a `filecheck` kobject with `check`, `fix`, and `set` attributes. Stores parse the attribute name into an operation, parse a positive numeric inode or queue length, reject duplicates among pending entries, enforce the queue maximum, optionally erase the oldest completed entry, enqueue an in-progress entry, then synchronously call `ocfs2_iget` with check or fix flags. Shows render the current max for `set` or a table of inode, done flag, and error string for matching check/fix entries. Removal deletes the kobject, waits for release completion, and frees only completed entries.

State and persistence behavior: queue state is in memory under `fc_lock`: maximum size, current size, completed count, and list of recent entries. File repair/check persistence is delegated to `ocfs2_iget` with `OCFS2_FI_FLAG_FILECHECK_CHK` or `OCFS2_FI_FLAG_FILECHECK_FIX`, which may validate or repair on-disk inode metadata. The sysfs kobject lifetime is guarded with a completion.

Dependencies and integration points: integrates Linux sysfs/kobject operations, OCFS2 superblock device kset, inode loading/check logic, stackglue-visible filecheck errors, and masklog. It is invoked from superblock lifecycle code, not normal file I/O.

Risks: `ocfs2_filecheck_args_get_long` copies `count` bytes into a fixed buffer after the caller enforces `count < 24`; that guard must remain. Queue manipulation assumes callers hold `fc_lock` for duplicate/erase/list updates. `ocfs2_filecheck_sysfs_free` BUGs if removal sees unfinished entries, so teardown must not race an active store. The operation is synchronous despite recording an in-progress entry, so slow inode checks can make sysfs writes block.

Test signals: create/remove sysfs on mount/unmount; write valid and invalid inode numbers to `check` and `fix`; read result tables; duplicate pending request rejection; queue-full `-EAGAIN`; queue-size bounds 10 to 100; shrinking queue with completed entries; read-only/fix failure statuses; invalid inode, block ECC/block number/valid flag/generation errors from inode check; and concurrent sysfs readers/writers during unmount.
