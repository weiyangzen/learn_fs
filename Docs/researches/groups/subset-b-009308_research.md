# subset-b-009308 research

Grouped research report for LTP syscall tests from `statx` through `utils`. Each section preserves the exact source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx02.c

Purpose: This code tests the following flags with statx syscall: - AT_EMPTY_PATH - AT_SYMLINK_NOFOLLOW A test file and a link for it is created. To check empty path flag, test file fd alone is passed. Predefined size of testfile is checked against obtained value. To check symlink no follow flag, the linkname is statxed. To ensure that link is not dereferenced, obtained inode is compared with test file inode.

Important APIs/types/functions: includes `stdio.h`, `inttypes.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `symlink`, `syscall`; defines `test_empty_path`, `test_sym_link`, `run`, `setup`, `cleanup`; uses constants `AT_EMPTY_PATH`, `AT_FDCWD`, `AT_SYMLINK_NOFOLLOW`, `O_CREAT`, `O_RDWR`.

Control flow centers on `test_empty_path`, `test_sym_link`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_tmpdir` into the runner.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdio.h`, `inttypes.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/stat.h`, `lapi/fcntl.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx03.c

Purpose: Test basic error handling of statx syscall: - EBADF - Bad file descriptor - EFAULT - Bad address - EINVAL - Invalid argument - ENOENT - No such file or directory - ENOTDIR - Not a directory - ENAMETOOLONG - Filename too long

Important APIs/types/functions: includes `stdio.h`, `string.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_get_bad_addr.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `syscall`; defines `run_test`, `setup`; uses constants `AT_FDCWD`, `EBADF`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `O_CREAT`, `O_RDWR`.

Control flow centers on `run_test`, `setup`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_tmpdir` into the runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdio.h`, `string.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_get_bad_addr.h`, `lapi/stat.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx04.c

Purpose: Test whether the kernel properly advertises support for statx() attributes: - STATX_ATTR_COMPRESSED: The file is compressed by the filesystem. - STATX_ATTR_IMMUTABLE: The file cannot be modified. - STATX_ATTR_APPEND: The file can only be opened in append mode for writing. - STATX_ATTR_NODUMP: File is not a candidate for backup when a backup program such as dump(8) is run. xfs filesystem doesn't support STATX_ATTR_COMPRESSED flag, so we only test three other flags. ext2, ext4, btrfs, xfs and tmpfs support statx syscall since the following commit commit 93bc420ed41df63a18ae794101f7cbf45226a6ef Date: Mon Feb 18 09:07:02 2019 +0800 ext2: support statx syscall commit 99652ea56a4186bc5bf8a3721c5353f41b35ebcb Date: Fri Mar 31 18:31:56 2017 +0100 ext4: Add statx support commit 04a87e3472828f769a93655d7c64a27573bdbc2c Date: Fri May 12 15:07:43 201

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`, `lapi/fs.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `syscall`, `ioctl`; defines `setup`, `run`; uses constants `AT_FDCWD`, `ENOTTY`, `FS_IOC_`, `FS_IOC_GETFLAGS`, `O_DIRECTORY`, `O_RDONLY`, `STATX_ATTR_APPEND`, `STATX_ATTR_COMPRESSED`, `STATX_ATTR_IMMUTABLE`, `STATX_ATTR_NODUMP`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.needs_root`, `.all_filesystems`, `.mount_device`, `.mntpoint`, `.skip_filesystems`, `.tags` into the runner. Named case hints include `fuse`, `linux-git`. Error-path expectations include `ENOTTY`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdlib.h`, `tst_test.h`, `lapi/fs.h`, `lapi/stat.h`, `lapi/fcntl.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_EXP_PASS_SILENT`, `TST_RET`, `TTERRNO`; checks errno values `ENOTTY`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx05.c

Purpose: Test statx syscall with STATX_ATTR_ENCRYPTED flag, setting a key is required for the file to be encrypted by the filesystem. e4crypt is used to set the encrypt flag (currently supported only by ext4). Two directories are tested. First directory has all flags set. Second directory has no flags set. Minimum e2fsprogs version required is 1.43.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `sys/types.h`, `sys/wait.h`, `tst_test.h`, `lapi/fs.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `syscall`; defines `test_flagged`, `test_unflagged`, `run`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `STATX_ATTR_ENCRYPTED`.

Control flow centers on `test_flagged`, `test_unflagged`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_root`, `.needs_device`, `.mntpoint`, `.filesystems`, `.needs_cmds` into the runner. Named case hints include `-O encrypt`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdlib.h`, `stdio.h`, `sys/types.h`, `sys/wait.h`, `tst_test.h`, `lapi/fs.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TCONF`, `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx06.c

Purpose: Test the following file timestamps of statx syscall: - btime - The time before and after the execution of the create system call is noted. - mtime - The time before and after the execution of the write system call is noted. - atime - The time before and after the execution of the read system call is noted. - ctime - The time before and after the execution of the chmod system call is noted.

Important APIs/types/functions: includes `stdio.h`, `time.h`, `tst_test.h`, `tst_safe_clocks.h`, `tst_safe_macros.h`, `tst_timer.h`, `lapi/stat.h`, `lapi/mount.h`; exercises `statx`, `syscall`, `time`, `mount`, `read`, `write`, `chmod`; defines `timestamp_to_timespec`, `clock_wait_tick`, `create_file`, `write_file`, `read_file`, `change_mode`, `test_statx`, `cleanup`; uses constants `AT_FDCWD`, `CLOCK_REALTIME`, `CLOCK_REALTIME_COARSE`, `O_CREAT`, `O_RDWR`, `STATX_BASIC_STATS`, `STATX_BTIME`.

Control flow centers on `timestamp_to_timespec`, `clock_wait_tick`, `create_file`, `write_file`, `read_file`, `change_mode`, `test_statx`, `cleanup`. The `struct tst_test` registration wires `.cleanup`, `.tcnt`, `.test`, `.needs_root`, `.mntpoint`, `.mount_device`, `.filesystems` into the runner. Named case hints include `-I`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdio.h`, `time.h`, `tst_test.h`, `tst_safe_clocks.h`, `tst_safe_macros.h`, `tst_timer.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx07.c

Purpose: This code tests the following flags: - AT_STATX_FORCE_SYNC - AT_STATX_DONT_SYNC By exportfs cmd creating NFS setup. A test file is created in server folder and statx is being done in client folder. BY AT_STATX_SYNC_AS_STAT getting predefined mode value. Then, by using AT_STATX_FORCE_SYNC getting new updated vaue from server file changes. BY AT_STATX_SYNC_AS_STAT getting predefined mode value. AT_STATX_FORCE_SYNC is called to create cache data of the file. Then, by using DONT_SYNC_FILE getting old cached data in client folder, but mode has been chaged in server file. The support for SYNC flags was implemented in NFS in: 9ccee940bd5b ("Support statx() mask and query flags parameters")

Important APIs/types/functions: includes `netdb.h`, `stdio.h`, `stdlib.h`, `errno.h`, `linux/limits.h`, `sys/mount.h`, `tst_test.h`, `lapi/stat.h`; exercises `statx`, `sync`, `umask`, `mount`; defines `get_mode`, `test_statx`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `AT_STATX_DONT_SYNC`, `AT_STATX_FORCE_SYNC`, `AT_STATX_SYNC_AS_STAT`, `ECONNREFUSED`, `EOPNOTSUPP`, `ETIMEDOUT`, `STATX_BASIC_STATS`.

Control flow centers on `get_mode`, `test_statx`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_tmpdir`, `.filesystems`, `.needs_root`, `.needs_cmds` into the runner. Error-path expectations include `ECONNREFUSED`, `EOPNOTSUPP`, `ETIMEDOUT`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `netdb.h`, `stdio.h`, `stdlib.h`, `errno.h`, `linux/limits.h`, `sys/mount.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`; checks errno values `ECONNREFUSED`, `EOPNOTSUPP`, `ETIMEDOUT`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx08.c

Purpose: This case tests whether the attributes field of statx received expected value by using flags in the stx_attributes_mask field of statx. File set with following flags by using SAFE_IOCTL: - STATX_ATTR_COMPRESSED: The file is compressed by the filesystem. - STATX_ATTR_IMMUTABLE: The file cannot be modified. - STATX_ATTR_APPEND: The file can only be opened in append mode for writing. - STATX_ATTR_NODUMP: File is not a candidate for backup when a backup program such as dump(8) is run. Two directories are tested. First directory has all flags set. Second directory has no flags set. ntfs3g fuse fs returns wrong errno for unimplemented ioctls

Important APIs/types/functions: includes `tst_test.h`, `lapi/fs.h`, `stdlib.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `ioctl`; defines `run`, `caid_flags_setup`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `ENOTTY`, `FS_APPEND_FL`, `FS_COMPR_FL`, `FS_IMMUTABLE_FL`, `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_NODUMP_FL`, `O_DIRECTORY`, `O_RDONLY`, `STATX_ATTR_APPEND`, `STATX_ATTR_COMPRESSED`, `STATX_ATTR_IMMUTABLE`, `STATX_ATTR_NODUMP`.

Control flow centers on `run`, `caid_flags_setup`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_root`, `.all_filesystems`, `.mount_device`, `.mntpoint` into the runner. Error-path expectations include `ENOTTY`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `tst_test.h`, `lapi/fs.h`, `stdlib.h`, `lapi/stat.h`, `lapi/fcntl.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; checks errno values `ENOTTY`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx09.c

Purpose: This code tests if STATX_ATTR_VERITY flag in the statx attributes is set correctly. The statx() system call sets STATX_ATTR_VERITY if the file has fs-verity enabled. This can perform better than FS_IOC_GETFLAGS and FS_IOC_MEASURE_VERITY because it doesn't require opening the file, and opening verity files can be expensive. Minimum Linux version required is v5.5.

Important APIs/types/functions: includes `sys/mount.h`, `stdlib.h`, `stdio.h`, `tst_test.h`, `lapi/fs.h`, `lapi/fsverity.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `ioctl`, `mount`; defines `test_flagged`, `test_unflagged`, `run`, `flag_setup`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `EINVAL`, `ENOTTY`, `EOPNOTSUPP`, `FS_IOC_ENABLE_VERITY`, `FS_IOC_GETFLAGS`, `FS_IOC_MEASURE_VERITY`, `FS_VERITY_FL`, `FS_VERITY_HASH_ALG_SHA256`, `O_RDONLY`, `STATX_ATTR_VERITY`.

Control flow centers on `test_flagged`, `test_unflagged`, `run`, `flag_setup`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_root`, `.needs_device`, `.mntpoint`, `.filesystems`, `.needs_kconfigs`, `.needs_cmds` into the runner. Named case hints include `-O verity`, `CONFIG_FS_VERITY`. Error-path expectations include `EINVAL`, `ENOTTY`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `sys/mount.h`, `stdlib.h`, `stdio.h`, `tst_test.h`, `lapi/fs.h`, `lapi/fsverity.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_EXP_PASS`, `TST_RET`; checks errno values `EINVAL`, `ENOTTY`, `EOPNOTSUPP`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx10.c

Purpose: It is a basic test for STATX_DIOALIGN mask on ext4 and xfs filesystem. - STATX_DIOALIGN Want stx_dio_mem_align and stx_dio_offset_align value Check these two values are nonzero under dio situation when STATX_DIOALIGN in the request mask. On ext4, files that use certain filesystem features (data journaling, encryption, and verity) fall back to buffered I/O. But ltp creates own filesystem by enabling mount_device in tst_test struct. If we set block device to LTP_DEV environment, we use this block device to mount by using default mount option. Otherwise, use loop device to simuate it. So it can avoid these above situations and don't fall back to buffered I/O. Minimum Linux version required is v6.1.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`, `stdlib.h`, `stdbool.h`, `tst_test.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `mount`, `open`; defines `verify_statx`, `setup`; uses constants `AT_FDCWD`, `EINVAL`, `O_DIRECT`, `O_RDWR`, `STATX_DIOALIGN`.

Control flow centers on `verify_statx`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.needs_root`, `.mntpoint`, `.mount_device`, `.all_filesystems` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `sys/types.h`, `unistd.h`, `stdlib.h`, `stdbool.h`, `tst_test.h`, `lapi/stat.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_EXP_PASS_SILENT`; checks errno values `EINVAL`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx11.c

Purpose: It is a basic test for STATX_DIOALIGN mask on block device. - STATX_DIOALIGN Want stx_dio_mem_align and stx_dio_offset_align value These two values are tightly coupled to the kernel's current DIO restrictions on block devices. Minimum Linux version required is v6.1. This test is tightly coupled to the kernel's current DIO restrictions on block devices. The general rule of DIO needing to be aligned to the block device's logical block size was relaxed to allow user buffers (but not file offsets) aligned to the DMA alignment instead. See v6.0 commit bf8d08532bc1 ("iomap: add support for dma aligned direct-io") and they are subject to further change in the future. Also can see commit 2d985f8c6b9 ("vfs: support STATX_DIOALIGN on block devices).

Important APIs/types/functions: includes `sys/types.h`, `sys/mount.h`, `unistd.h`, `stdlib.h`, `stdbool.h`, `stdio.h`, `tst_test.h`, `lapi/stat.h`; exercises `statx`, `sysfs`, `mount`; defines `verify_statx`, `setup`; uses constants `AT_FDCWD`, `STATX_DIOALIGN`.

Control flow centers on `verify_statx`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.needs_device`, `.needs_root` into the runner.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `sys/types.h`, `sys/mount.h`, `unistd.h`, `stdlib.h`, `stdbool.h`, `stdio.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TCONF`, `TST_ASSERT_ULONG`, `TST_EXP_PASS_SILENT`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx12.c

Purpose: It is a basic test for STATX_ATTR_MOUNT_ROOT flag. This flag indicates whether the path or fd refers to the root of a mount or not. Minimum Linux version required is v5.8.

Important APIs/types/functions: includes `unistd.h`, `stdlib.h`, `stdbool.h`, `stdio.h`, `tst_test.h`, `lapi/stat.h`; exercises `statx`, `mount`; defines `verify_statx`, `setup`, `cleanup`; uses constants `AT_EMPTY_PATH`, `AT_FDCWD`, `O_DIRECTORY`, `O_RDWR`, `STATX_ATTR_MOUNT_ROOT`.

Control flow centers on `verify_statx`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.setup`, `.cleanup`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.tcnt` into the runner.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `unistd.h`, `stdlib.h`, `stdbool.h`, `stdio.h`, `tst_test.h`, `lapi/stat.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_EXP_PASS_SILENT`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/stime/Makefile

Purpose: build metadata for the `stime` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime01.c

Purpose: Test Description: Verify that the system call stime() successfully sets the system's idea of date and time if invoked by "root" user. Expected Result: stime() should succeed to set the system data/time to the specified time. 07/2001 John George -Ported

Important APIs/types/functions: includes `time.h`, `sys/time.h`, `tst_test.h`, `stime_var.h`; exercises `stime`, `time`; defines `run`, `setup`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test_all`, `.needs_root`, `.setup`, `.test_variants` into the runner.

State and persistence behavior: Runtime state is the system wall clock. The tests deliberately change or attempt to change global system time and rely on privilege transitions plus libc/raw syscall dispatch.

Dependencies and integration points: Depends on `stime_var.h`, libc `stime()` when available, raw `__NR_stime` fallback, root privileges for success paths, and nobody-user credential switching for EPERM paths. Direct include dependencies include `time.h`, `sys/time.h`, `tst_test.h`, `stime_var.h`.

Risks and test signals: Changing system time is globally disruptive; success tests require root and failure tests rely on clean credential transitions and platform support for obsolete `stime()`. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime02.c

Purpose: Test Description: Verify that the system call stime() fails to set the system's idea of data and time if invoked by "non-root" user. Expected Result: stime() should fail with return value -1 and set errno to EPERM. 07/2001 John George -Ported

Important APIs/types/functions: includes `sys/types.h`, `errno.h`, `time.h`, `pwd.h`, `tst_test.h`, `stime_var.h`; exercises `stime`, `time`; defines `run`, `setup`; uses constants `EPERM`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.needs_root`, `.test_variants` into the runner. Error-path expectations include `EPERM`.

State and persistence behavior: Runtime state is the system wall clock. The tests deliberately change or attempt to change global system time and rely on privilege transitions plus libc/raw syscall dispatch.

Dependencies and integration points: Depends on `stime_var.h`, libc `stime()` when available, raw `__NR_stime` fallback, root privileges for success paths, and nobody-user credential switching for EPERM paths. Direct include dependencies include `sys/types.h`, `errno.h`, `time.h`, `pwd.h`, `tst_test.h`, `stime_var.h`.

Risks and test signals: Changing system time is globally disruptive; success tests require root and failure tests rely on clean credential transitions and platform support for obsolete `stime()`. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EPERM`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime_var.h

Purpose: Shared compatibility layer for stime tests; it reports whether libc `stime()` or the raw `__NR_stime` syscall is used and normalizes unsupported platforms into LTP configuration failures.

Important APIs/types/functions: includes `sys/time.h`, `config.h`, `tst_timer.h`, `lapi/syscalls.h`; defines `do_stime`, `stime_info`; touches `stime`, `syscall`, `time`, `raw syscall path`; uses constants/macros such as `TCONF`, `TINFO`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is the system wall clock. The tests deliberately change or attempt to change global system time and rely on privilege transitions plus libc/raw syscall dispatch.

Dependencies and integration points: Depends on `stime_var.h`, libc `stime()` when available, raw `__NR_stime` fallback, root privileges for success paths, and nobody-user credential switching for EPERM paths. Direct includes: `sys/time.h`, `config.h`, `tst_timer.h`, `lapi/syscalls.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime_var.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/string/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/string/Makefile

Purpose: build metadata for the `string` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/string/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/string/string01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/string/string01.c

Purpose: (at your option) any later version. This program is distributed in the hope that it will be useful, Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA 01/02/2003 Port to LTP avenkat@us.ibm.com 06/30/2001 Port to Linux nsharoff@us.ibm.com string01.c - check string functions. CALLS strchr, strrchr, strcat, strcmp, strcpy, strlen, strncat, strncmp, strncpy ALGORITHM Test functionality of the string functions: (strchr, strrchr, strcat, strcmp, strcpy, strlen, strncat, strncmp, strncpy )

Important APIs/types/functions: includes `stdio.h`, `sys/types.h`, `string.h`, `errno.h`, `stdlib.h`, `test.h`; exercises `write`; defines `setup`, `blenter`, `blexit`, `anyfail`, `main`.

Control flow centers on `setup`, `blenter`, `blexit`, `anyfail`, `main`. This is an older harness test using `tst_parse_opts()`, `TEST_LOOPING()`, and explicit cleanup. Named case hints include `12345`.

State and persistence behavior: Runtime state is only process memory and the legacy LTP result counters; the file is a placeholder-style legacy syscall-suite test rather than a kernel state exercise.

Dependencies and integration points: Depends on the legacy LTP `test.h` harness and option/result helpers; it has no modern `struct tst_test` integration. Direct include dependencies include `stdio.h`, `sys/types.h`, `string.h`, `errno.h`, `stdlib.h`, `test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/string/string01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/Makefile

Purpose: build metadata for the `swapoff` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; LTPLIBS = swap; include $(top_srcdir)/include/mk/testcases.mk; LTPLDLIBS  = -lltpswap; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`, plus directory-local linker flags. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff01.c

Purpose: Check that swapoff() succeeds.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapoff`, `raw syscall path`; defines `verify_swapoff`, `setup`.

Control flow centers on `verify_swapoff`, `setup`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.test_all`, `.timeout`, `.setup` into the runner.

State and persistence behavior: Runtime state is swap activation state for temporary swapfiles, user credentials, mounted filesystem support for swapfiles, and cleanup that must leave no active swap area behind.

Dependencies and integration points: Depends on swapfile creation helpers, raw `swapoff` syscall wrappers when libc lacks the call, root privileges, mounted filesystem support, and credential switching for permission failures. Direct include dependencies include `unistd.h`, `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`.

Risks and test signals: Leaking active swapfiles or running on filesystems that cannot host swapfiles can affect the host, so setup/cleanup ordering is critical. Test signals: reports through `TERRNO`, `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff02.c

Purpose: This test case checks whether swapoff(2) system call returns 1. EINVAL when the path does not exist 2. ENOENT when the path exists but is invalid 3. EPERM when user is not a superuser

Important APIs/types/functions: includes `errno.h`, `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapoff`, `raw syscall path`; defines `setup01`, `cleanup01`, `verify_swapoff`, `setup`; uses constants `EINVAL`, `ENOENT`, `EPERM`.

Control flow centers on `setup01`, `cleanup01`, `verify_swapoff`, `setup`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.test`, `.tcnt`, `.setup` into the runner. Named case hints include `path does not exist`, `Invalid file`, `Permission denied`. Error-path expectations include `EINVAL`, `ENOENT`, `EPERM`.

State and persistence behavior: Runtime state is swap activation state for temporary swapfiles, user credentials, mounted filesystem support for swapfiles, and cleanup that must leave no active swap area behind.

Dependencies and integration points: Depends on swapfile creation helpers, raw `swapoff` syscall wrappers when libc lacks the call, root privileges, mounted filesystem support, and credential switching for permission failures. Direct include dependencies include `errno.h`, `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`.

Risks and test signals: Leaking active swapfiles or running on filesystems that cannot host swapfiles can affect the host, so setup/cleanup ordering is critical. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`; checks errno values `EINVAL`, `ENOENT`, `EPERM`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapon/Makefile

Purpose: build metadata for the `swapon` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; LTPLIBS = swap; include $(top_srcdir)/include/mk/testcases.mk; LTPLDLIBS  = -lltpswap; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`, plus directory-local linker flags. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon01.c

Purpose: Checks that swapon() succeds with swapfile. Testing on all filesystems which support swap file.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapon`, `raw syscall path`; defines `verify_swapon`, `setup`.

Control flow centers on `verify_swapon`, `setup`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.needs_root`, `.all_filesystems`, `.test_all`, `.timeout`, `.setup` into the runner. Named case hints include `memory`.

State and persistence behavior: Runtime state is active swap areas, `/proc/meminfo` accounting, cgroup memory limits where present, temporary swapfile contents, and the kernel-wide maximum number of swapfiles.

Dependencies and integration points: Depends on swapfile helpers, cgroup/meminfo helpers for memory-pressure checks, root privileges, mounted filesystem support, and reliable cleanup through `swapoff()`. Direct include dependencies include `unistd.h`, `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`.

Risks and test signals: Swap tests can perturb host memory behavior and hit kernel-global swap limits; cleanup failures leave persistent system state. Test signals: reports through `TBROK`, `TERRNO`, `TINFO`, `TST_EXP_PASS`, `TST_PASS`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon02.c

Purpose: This test case checks whether swapon(2) system call returns: - ENOENT when the path does not exist - EINVAL when the path exists but is invalid - EPERM when user is not a superuser - EBUSY when the specified path is already being used as a swap area

Important APIs/types/functions: includes `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapoff`, `swapon`, `raw syscall path`; defines `setup`, `cleanup`, `verify_swapon`; uses constants `EBUSY`, `EINVAL`, `ENOENT`, `EPERM`.

Control flow centers on `setup`, `cleanup`, `verify_swapon`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.test`, `.tcnt`, `.setup`, `.cleanup` into the runner. Named case hints include `Path does not exist`, `Invalid path`, `Permission denied`, `File already used`. Error-path expectations include `EBUSY`, `EINVAL`, `ENOENT`, `EPERM`.

State and persistence behavior: Runtime state is active swap areas, `/proc/meminfo` accounting, cgroup memory limits where present, temporary swapfile contents, and the kernel-wide maximum number of swapfiles.

Dependencies and integration points: Depends on swapfile helpers, cgroup/meminfo helpers for memory-pressure checks, root privileges, mounted filesystem support, and reliable cleanup through `swapoff()`. Direct include dependencies include `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`.

Risks and test signals: Swap tests can perturb host memory behavior and hit kernel-global swap limits; cleanup failures leave persistent system state. Test signals: reports through `TERRNO`, `TFAIL`, `TST_EXP_FAIL`, `TST_RET`; checks errno values `EBUSY`, `EINVAL`, `ENOENT`, `EPERM`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon03.c

Purpose: Created by <rsalveti@linux.vnet.ibm.com> Test checks whether :manpage:`swapon(2)` system call returns EPERM when the maximum number of swap files are already in use. NOTE: test does not try to calculate MAX_SWAPFILES from the internal kernel implementation, instead make sure at least 15 swaps were created before the maximum of swaps was reached. MAX_SWAPFILES from the internal kernel implementation is currently <23, 29>, depending on kernel configuration (see man swapon(2)). Chose small enough value for future changes. Create the swapfile

Important APIs/types/functions: includes `stdio.h`, `errno.h`, `stdlib.h`, `sys/wait.h`, `sys/swap.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapoff`, `swapon`; defines `setup_swap`, `check_and_swapoff`, `clean_swap`, `verify_swapon`, `setup`, `cleanup`; uses constants `EPERM`.

Control flow centers on `setup_swap`, `check_and_swapoff`, `clean_swap`, `verify_swapon`, `setup`, `cleanup`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.test_all`, `.setup`, `.cleanup` into the runner. Error-path expectations include `EPERM`.

State and persistence behavior: Runtime state is active swap areas, `/proc/meminfo` accounting, cgroup memory limits where present, temporary swapfile contents, and the kernel-wide maximum number of swapfiles.

Dependencies and integration points: Depends on swapfile helpers, cgroup/meminfo helpers for memory-pressure checks, root privileges, mounted filesystem support, and reliable cleanup through `swapoff()`. Direct include dependencies include `stdio.h`, `errno.h`, `stdlib.h`, `sys/wait.h`, `sys/swap.h`, `tst_test.h`.

Risks and test signals: Swap tests can perturb host memory behavior and hit kernel-global swap limits; cleanup failures leave persistent system state. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TST_EXP_FAIL`; checks errno values `EPERM`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/switch/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/switch/Makefile

Purpose: build metadata for the `switch` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/switch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/switch/endian_switch01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/switch/endian_switch01.c

Purpose: Test little-endian mode switch system call. Requires a 64-bit processor that supports little-endian mode,such as POWER6. Make minimal call to 0x1ebe. If we get ENOSYS then syscall is not available, likely because of: commit 727f13616c45 ("powerpc: Disable the fast-endian switch syscall by default") If we get any other outcome, including crashes with various signals, then we assume syscall is available and carry on with the test. HAVE_GETAUXVAL

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `elf.h`, `sys/types.h`, `sys/wait.h`, `tst_test.h`; exercises `syscall`, `raw syscall path`; defines `check_le_switch_supported`, `test_le_switch`, `endian_test`; uses constants `AT_HWCAP`, `ENOSYS`.

Control flow centers on `check_le_switch_supported`, `test_le_switch`, `endian_test`. The `struct tst_test` registration wires `.test_all` into the runner. Error-path expectations include `ENOSYS`.

State and persistence behavior: Runtime state is PowerPC endian execution mode in a forked child and whether the kernel/CPU supports little-endian switching.

Dependencies and integration points: Depends on PowerPC-specific `syscall(__NR_switch_endian)`, fork/wait helpers, and architecture guards that skip unsupported platforms. Direct include dependencies include `errno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `elf.h`, `sys/types.h`.

Risks and test signals: Architecture guards are essential because the syscall is PowerPC-specific and child crashes are an expected way to isolate unsupported mode changes. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_TEST_TCONF`; checks errno values `ENOSYS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/switch/endian_switch01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlink/Makefile

Purpose: build metadata for the `symlink` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink02.c

Purpose: Check the basic functionality of the symlink() system call.

Important APIs/types/functions: includes `tst_test.h`; exercises `symlink`; defines `verify_symlink`, `setup`.

Control flow centers on `verify_symlink`, `setup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.test_all` into the runner.

State and persistence behavior: Runtime state is pathname namespace fixtures: regular files, nonexistent targets, symlinks, long paths, permissions, and lstat-visible link metadata.

Dependencies and integration points: Depends on LTP filesystem fixtures, safe path helpers, legacy bad-address helpers in old tests, and lstat/readlink-visible symlink semantics. Direct include dependencies include `tst_test.h`.

Risks and test signals: Path length, permission, bad-address, and legacy harness behavior can vary; the durable signal is correct errno or lstat-visible link state. Test signals: reports through `TFAIL`, `TST_EXP_POSITIVE`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink03.c

Purpose: (at your option) any later version. This program is distributed in the hope that it will be useful, Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA Test Name : symlink03 Test Description : Verify that, 1) symlink(2) returns -1 and sets errno to EACCES if search/write permission is denied in the directory where the symbolic link is being created. 2) symlink(2) returns -1 and sets errno to EEXIST if the specified symbolic link already exists. 3) symlink(2) returns -1 and sets errno to EFAULT if the specified file or symbolic link points to invalid address. 4) symlink(2) returns -1 and sets errno to ENAMETOOLONG if the pathname component of symbolic link is too long (ie, > PATH_MAX). 5) symlink(2) returns -1 and sets errno to ENOTDIR if the directory component in pathname of symbolic link is not a directory. 6) s

Important APIs/types/functions: includes `stdio.h`, `sys/types.h`, `fcntl.h`, `sys/mman.h`, `errno.h`, `string.h`, `signal.h`, `sys/stat.h`; exercises `symlink`, `syscall`, `times`, `fork`, `write`, `open`, `close`, `chmod`; defines `no_setup`, `setup1`, `setup2`, `setup3`, `longpath_setup`, `setup`, `cleanup`, `main`; uses constants `EACCES`, `EEXIST`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `O_CREAT`, `O_RDWR`, `SIGUSR1`.

Control flow centers on `no_setup`, `setup1`, `setup2`, `setup3`, `longpath_setup`, `setup`, `cleanup`, `main`. This is an older harness test using `tst_parse_opts()`, `TEST_LOOPING()`, and explicit cleanup. Error-path expectations include `EACCES`, `EEXIST`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is pathname namespace fixtures: regular files, nonexistent targets, symlinks, long paths, permissions, and lstat-visible link metadata.

Dependencies and integration points: Depends on LTP filesystem fixtures, safe path helpers, legacy bad-address helpers in old tests, and lstat/readlink-visible symlink semantics. Direct include dependencies include `stdio.h`, `sys/types.h`, `fcntl.h`, `sys/mman.h`, `errno.h`, `string.h`.

Risks and test signals: Path length, permission, bad-address, and legacy harness behavior can vary; the durable signal is correct errno or lstat-visible link state. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_TOTAL`; checks errno values `EACCES`, `EEXIST`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink04.c

Purpose: Check that a symbolic link may point to an existing file or to a nonexistent one.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `tst_test.h`; exercises `symlink`; defines `setup`, `verify_symlink`.

Control flow centers on `setup`, `verify_symlink`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.test`, `.needs_tmpdir` into the runner.

State and persistence behavior: Runtime state is pathname namespace fixtures: regular files, nonexistent targets, symlinks, long paths, permissions, and lstat-visible link metadata.

Dependencies and integration points: Depends on LTP filesystem fixtures, safe path helpers, legacy bad-address helpers in old tests, and lstat/readlink-visible symlink semantics. Direct include dependencies include `stdlib.h`, `stdio.h`, `tst_test.h`.

Risks and test signals: Path length, permission, bad-address, and legacy harness behavior can vary; the durable signal is correct errno or lstat-visible link state. Test signals: reports through `TFAIL`, `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/Makefile

Purpose: build metadata for the `symlinkat` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/symlinkat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/symlinkat01.c

Purpose: (at your option) any later version. This program is distributed in the hope that it will be useful, Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA symlinkat01.c DESCRIPTION This test case will verify basic function of symlinkat added by kernel 2.6.16 or up. Author Yi Yang <yyangcdl@cn.ibm.com> 08/25/2006 Created first by Yi Yang <yyangcdl@cn.ibm.com> relative paths abs path at dst relative paths to cwd

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`, `string.h`, `signal.h`; exercises `symlinkat`, `time`, `unlink`, `write`, `close`, `raw syscall path`; defines `setup`, `cleanup`, `setup_every_copy`, `mysymlinkat_test`, `mysymlinkat`, `main`; uses constants `AT_FDCWD`, `EBADF`, `ENOENT`, `ENOTDIR`, `O_CREAT`, `O_DIRECTORY`, `O_EXCL`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `setup`, `cleanup`, `setup_every_copy`, `mysymlinkat_test`, `mysymlinkat`, `main`. This is an older harness test using `tst_parse_opts()`, `TEST_LOOPING()`, and explicit cleanup. Named case hints include `../`. Error-path expectations include `EBADF`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is directory file descriptors plus relative symlink creation and readback in a temporary directory tree.

Dependencies and integration points: Depends on raw `symlinkat` syscall wrappers, directory fd setup, legacy LTP looping harness, and temporary directory cleanup. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EBADF`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/symlinkat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync/Makefile

Purpose: build metadata for the `sync` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync/sync01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync/sync01.c

Purpose: sync03 It basically tests sync() to sync test file having large dirty file pages to block device. Also, it tests all supported filesystems on a test block device.

Important APIs/types/functions: includes `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`; exercises `sync`; defines `verify_sync`; uses constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_sync`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`, `.mntpoint`, `.test_all` into the runner. Named case hints include `tmpfs`.

State and persistence behavior: Runtime state is dirty page cache and block-device write counters around `sync()`/`tst_dev_sync()` on a mounted test filesystem.

Dependencies and integration points: Depends on a mounted block device, dirtying helpers such as `tst_fill_fd()`, device write counters, and filesystem skip lists. Direct include dependencies include `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`.

Risks and test signals: Writeback counters are timing- and filesystem-sensitive; delayed or background writeback can create noisy signals. Test signals: reports through `TFAIL`, `TPASS`, `TST_MB`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync/sync01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/Makefile

Purpose: build metadata for the `sync_file_range` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk; CFLAGS += -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/check_sync_file_range.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/check_sync_file_range.h

Purpose: Shared probe for `sync_file_range()` availability; it calls the wrapper once and converts `ENOSYS` into an LTP configuration skip.

Important APIs/types/functions: defines `check_sync_file_range`; touches `sync_file_range`; uses constants/macros such as `EINVAL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is dirty file ranges, file descriptors, offsets, flags, and block-device write counters before and after `sync_file_range()`.

Dependencies and integration points: Depends on `check_sync_file_range.h`, raw syscall wrappers, mounted test devices for writeback observation, and ordinary temp files for error paths. Direct includes: none beyond consumers.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/check_sync_file_range.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range01.c

Purpose: Basic error conditions test for sync_file_range() system call, tests for: - EBADFD Wrong filedescriptor - ESPIPE Unsupported file descriptor - EINVAL Wrong offset - EINVAL Wrong nbytes - EINVAL Wrong flags

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `sys/utsname.h`, `endian.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `tst_test.h`; exercises `sync_file_range`, `raw syscall path`; defines `cleanup`, `setup`, `run_test`; uses constants `EBADF`, `EINVAL`, `ESPIPE`, `O_CREAT`, `O_RDWR`.

Control flow centers on `cleanup`, `setup`, `run_test`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test`, `.cleanup`, `.needs_tmpdir` into the runner. Error-path expectations include `EBADF`, `EINVAL`, `ESPIPE`.

State and persistence behavior: Runtime state is dirty file ranges, file descriptors, offsets, flags, and block-device write counters before and after `sync_file_range()`.

Dependencies and integration points: Depends on `check_sync_file_range.h`, raw syscall wrappers, mounted test devices for writeback observation, and ordinary temp files for error paths. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `sys/utsname.h`, `endian.h`, `fcntl.h`, `stdio.h`.

Risks and test signals: Range writeback behavior varies by filesystem and kernel; invalid-argument tests must distinguish unsupported syscall from real failure. Test signals: reports through `TCONF`, `TST_EXP_FAIL`; checks errno values `EBADF`, `EINVAL`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range02.c

Purpose: Tests if sync_file_range() does sync a test file range with a many dirty pages to a block device. Also, it tests all supported filesystems on a test block device. Fat does not support sparse files, we have to pre-fill the file so that the zero-filled start of the file has been written to disk before the test starts.

Important APIs/types/functions: includes `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`, `lapi/sync_file_range.h`, `check_sync_file_range.h`; exercises `sync`, `sync_file_range`, `write`; defines `verify_sync_file_range`, `run`, `setup`; uses constants `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `verify_sync_file_range`, `run`, `setup`. The `struct tst_test` registration wires `.tcnt`, `.needs_root`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`, `.mntpoint`, `.setup`, `.test` into the runner. Named case hints include `fuse`.

State and persistence behavior: Runtime state is dirty file ranges, file descriptors, offsets, flags, and block-device write counters before and after `sync_file_range()`.

Dependencies and integration points: Depends on `check_sync_file_range.h`, raw syscall wrappers, mounted test devices for writeback observation, and ordinary temp files for error paths. Direct include dependencies include `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`, `lapi/sync_file_range.h`.

Risks and test signals: Range writeback behavior varies by filesystem and kernel; invalid-argument tests must distinguish unsupported syscall from real failure. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_MB`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/Makefile

Purpose: build metadata for the `syncfs` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir             ?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/check_syncfs.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/check_syncfs.h

Purpose: Shared probe for `syncfs()` availability; it calls the wrapper once and converts missing syscall support into an LTP configuration skip.

Important APIs/types/functions: defines `check_syncfs`; touches `syncfs`; uses constants/macros such as `EINVAL`, `TCONF`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is dirty data tied to a specific mounted filesystem and file descriptor; only that filesystem should be flushed by `syncfs()`.

Dependencies and integration points: Depends on `check_syncfs.h`, raw syscall wrappers, mounted test devices, block write counters, and per-filesystem descriptor setup. Direct includes: none beyond consumers.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/check_syncfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/syncfs01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/syncfs01.c

Purpose: Test syncfs It basically tests syncfs() to sync filesystem having large dirty file pages to block device. Also, it tests all supported filesystems on a test block device.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`, `lapi/syncfs.h`, `check_syncfs.h`; exercises `sync`, `syncfs`; defines `verify_syncfs`, `setup`; uses constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_syncfs`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`, `.mntpoint`, `.setup`, `.test_all` into the runner. Named case hints include `tmpfs`.

State and persistence behavior: Runtime state is dirty data tied to a specific mounted filesystem and file descriptor; only that filesystem should be flushed by `syncfs()`.

Dependencies and integration points: Depends on `check_syncfs.h`, raw syscall wrappers, mounted test devices, block write counters, and per-filesystem descriptor setup. Direct include dependencies include `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`, `lapi/syncfs.h`, `check_syncfs.h`.

Risks and test signals: Per-filesystem flush accounting is timing-sensitive and depends on block-device counter accuracy. Test signals: reports through `TFAIL`, `TPASS`, `TST_MB`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/syncfs01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syscall/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syscall/Makefile

Purpose: build metadata for the `syscall` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syscall/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syscall/syscall01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syscall/syscall01.c

Purpose: 01/02/2003 Port to LTP avenkat@us.ibm.com 06/30/2001 Port to Linux nsharoff@us.ibm.com Basic test for syscall(). Compare raw get{g,p,u}id results with their glibc wrappers.

Important APIs/types/functions: includes `unistd.h`, `sys/syscall.h`, `sys/types.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `syscall`, `raw syscall path`; defines `verify_getpid`, `verify_getuid`, `verify_getgid`, `verify_syscall`.

Control flow centers on `verify_getpid`, `verify_getuid`, `verify_getgid`, `verify_syscall`. The `struct tst_test` registration wires `.test`, `.tcnt` into the runner.

State and persistence behavior: Runtime state is the raw syscall ABI dispatch path and errno propagation for syscall numbers and arguments selected by the test.

Dependencies and integration points: Depends on libc `syscall()`, LTP errno/result helpers, and syscall numbers present for the target architecture. Direct include dependencies include `unistd.h`, `sys/syscall.h`, `sys/types.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syscall/syscall01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysconf/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysconf/Makefile

Purpose: build metadata for the `sysconf` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysconf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysconf/sysconf01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysconf/sysconf01.c

Purpose: (at your option) any later version. This program is distributed in the hope that it will be useful, Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA http://www.opengroup.org/onlinepubs/009695399/functions/sysconf.html sysconf01 : test for sysconf( get configurable system variables) sys call. USAGE : sysconf01 LTP Port * make sure we reset this as sysconf() will not

Important APIs/types/functions: includes `stdio.h`, `sys/types.h`, `errno.h`, `unistd.h`, `test.h`; exercises `syscall`, `sysconf`, `write`; defines `_test_sysconf`, `main`; uses constants `EINVAL`, `_SC_2_CHAR_TERM`, `_SC_2_C_BIND`, `_SC_2_C_DEV`, `_SC_2_C_VERSION`, `_SC_2_FORT_DEV`, `_SC_2_FORT_RUN`, `_SC_2_LOCALEDEF`, `_SC_2_SW_DEV`, `_SC_2_UPE`, `_SC_2_VERSION`, `_SC_AIO_MAX`, `_SC_AIO_PRIO_DELTA_MAX`, `_SC_ARG_MAX`.

Control flow centers on `_test_sysconf`, `main`. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is process-visible system configuration values returned by libc `sysconf()` for limits and POSIX options.

Dependencies and integration points: Depends on libc `sysconf()` and platform-specific `_SC_*` constants and limits. Direct include dependencies include `stdio.h`, `sys/types.h`, `errno.h`, `unistd.h`, `test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysconf/sysconf01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/Makefile

Purpose: build metadata for the `sysctl` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl01.c

Purpose: DESCRIPTION: Testcase for testing the basic functionality of sysctl(2) system call. This testcase attempts to read the kernel parameters by using sysctl({CTL_KERN, KERN_* }, ...) and compares it with the known values. get kernel name and information revert uname change in case of kGraft/livepatch

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `string.h`, `linux/version.h`, `sys/utsname.h`, `linux/unistd.h`, `linux/sysctl.h`, `tst_test.h`; exercises `sysctl`, `uname`, `read`, `raw syscall path`; defines `verify_sysctl`, `setup`.

Control flow centers on `verify_sysctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test` into the runner. Named case hints include `KERN_OSTYPE`, `KERN_OSRELEASE`, `KERN_VERSION`.

State and persistence behavior: Runtime state is legacy `_sysctl` kernel name tables and userspace buffers; modern kernels may disable or reject this deprecated interface.

Dependencies and integration points: Depends on `lapi/sysctl.h`, raw `_sysctl` availability, kernel config permitting the legacy syscall, and root privileges for some namespace/table access. Direct include dependencies include `errno.h`, `stdio.h`, `string.h`, `linux/version.h`, `sys/utsname.h`, `linux/unistd.h`.

Risks and test signals: The `_sysctl` syscall is deprecated and often disabled, so TCONF is a normal signal on modern kernels. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl03.c

Purpose: DESCRIPTION 1) Call sysctl(2) as a root user, and attempt to write data to the kernel_table[]. Since the table does not have write permissions even for the root, it should fail EPERM. 2) Call sysctl(2) as a non-root user, and attempt to write data to the kernel_table[]. Since the table does not have write permission for the regular user, it should fail with EPERM. NOTE: There is a documentation bug in 2.6.33-rc1 where unfortunately the behavior of sysctl(2) isn't properly documented, as discussed in detail in the following thread: http://sourceforge.net/mailarchive/message.php?msg_name=4B7BA24F.2010705%40linux.vnet.ibm.com. The documentation bug is filed as: https://bugzilla.kernel.org/show_bug.cgi?id=15446 . If you want the message removed, please ask your fellow kernel maintainer to fix their documentation. Thanks! -Ngie

Important APIs/types/functions: includes `sys/types.h`, `sys/wait.h`, `stdio.h`, `errno.h`, `unistd.h`, `linux/unistd.h`, `linux/sysctl.h`, `pwd.h`; exercises `sysctl`, `read`, `write`, `raw syscall path`; defines `verify_sysctl`, `setup`, `do_test`; uses constants `EACCES`, `EPERM`.

Control flow centers on `verify_sysctl`, `setup`, `do_test`. The `struct tst_test` registration wires `.needs_root`, `.setup`, `.test_all` into the runner. Error-path expectations include `EACCES`, `EPERM`.

State and persistence behavior: Runtime state is legacy `_sysctl` kernel name tables and userspace buffers; modern kernels may disable or reject this deprecated interface.

Dependencies and integration points: Depends on `lapi/sysctl.h`, raw `_sysctl` availability, kernel config permitting the legacy syscall, and root privileges for some namespace/table access. Direct include dependencies include `sys/types.h`, `sys/wait.h`, `stdio.h`, `errno.h`, `unistd.h`, `linux/unistd.h`.

Risks and test signals: The `_sysctl` syscall is deprecated and often disabled, so TCONF is a normal signal on modern kernels. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EACCES`, `EPERM`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl04.c

Purpose: DESCRIPTION 1) Call sysctl(2) with nlen set to 0, and expect ENOTDIR. 2) Call sysctl(2) with nlen greater than CTL_MAXNAME, and expect ENOTDIR. 3) Call sysctl(2) with the address of oldname outside the address space of the process, and expect EFAULT. 4) Call sysctl(2) with the address of soldval outside the address space of the process, and expect EFAULT.

Important APIs/types/functions: includes `stdio.h`, `errno.h`, `unistd.h`, `linux/unistd.h`, `linux/sysctl.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `sysctl`, `raw syscall path`; defines `verify_sysctl`; uses constants `EFAULT`, `ENOTDIR`.

Control flow centers on `verify_sysctl`. The `struct tst_test` registration wires `.tcnt`, `.test` into the runner. Error-path expectations include `EFAULT`, `ENOTDIR`.

State and persistence behavior: Runtime state is legacy `_sysctl` kernel name tables and userspace buffers; modern kernels may disable or reject this deprecated interface.

Dependencies and integration points: Depends on `lapi/sysctl.h`, raw `_sysctl` availability, kernel config permitting the legacy syscall, and root privileges for some namespace/table access. Direct include dependencies include `stdio.h`, `errno.h`, `unistd.h`, `linux/unistd.h`, `linux/sysctl.h`, `tst_test.h`.

Risks and test signals: The `_sysctl` syscall is deprecated and often disabled, so TCONF is a normal signal on modern kernels. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EFAULT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/Makefile

Purpose: build metadata for the `sysfs` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs01.c

Purpose: This test is run for option 1 for sysfs(2). Translate the filesystem identifier string fsname into a filesystem type index. option 1, buf holds fs name

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `syscall`, `sysfs`, `raw syscall path`; defines `verify_sysfs01`.

Control flow centers on `verify_sysfs01`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is the legacy `sysfs(2)` filesystem type registry and indexes/names returned through libc or raw syscall wrappers.

Dependencies and integration points: Depends on libc or raw `sysfs(2)` wrappers and kernel support for the deprecated filesystem type query API. Direct include dependencies include `errno.h`, `unistd.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The `sysfs(2)` API is obsolete and filesystem type ordering can vary across kernels. Test signals: reports through `TST_EXP_POSITIVE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs02.c

Purpose: This test is run for option 2 for sysfs(2). Translate the filesystem type index fs_index into a null-terminated filesystem identifier string. This string will be written to the buffer pointed to by buf. Make sure that buf has enough space to accept the string.

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `syscall`, `sysfs`, `raw syscall path`; defines `verify_sysfs02`.

Control flow centers on `verify_sysfs02`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is the legacy `sysfs(2)` filesystem type registry and indexes/names returned through libc or raw syscall wrappers.

Dependencies and integration points: Depends on libc or raw `sysfs(2)` wrappers and kernel support for the deprecated filesystem type query API. Direct include dependencies include `errno.h`, `unistd.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The `sysfs(2)` API is obsolete and filesystem type ordering can vary across kernels. Test signals: reports through `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs03.c

Purpose: This test is run for option 3 for sysfs(2). Return the total number of filesystem types currently present in the kernel.

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `syscall`, `sysfs`, `raw syscall path`; defines `verify_sysfs03`.

Control flow centers on `verify_sysfs03`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is the legacy `sysfs(2)` filesystem type registry and indexes/names returned through libc or raw syscall wrappers.

Dependencies and integration points: Depends on libc or raw `sysfs(2)` wrappers and kernel support for the deprecated filesystem type query API. Direct include dependencies include `errno.h`, `unistd.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The `sysfs(2)` API is obsolete and filesystem type ordering can vary across kernels. Test signals: reports through `TST_EXP_POSITIVE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs04.c

Purpose: This test case checks whether sysfs(2) system call returns appropriate error number for invalid option.

Important APIs/types/functions: includes `errno.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `syscall`, `sysfs`, `raw syscall path`; defines `verify_sysfs04`; uses constants `EINVAL`.

Control flow centers on `verify_sysfs04`. The `struct tst_test` registration wires `.test_all` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is the legacy `sysfs(2)` filesystem type registry and indexes/names returned through libc or raw syscall wrappers.

Dependencies and integration points: Depends on libc or raw `sysfs(2)` wrappers and kernel support for the deprecated filesystem type query API. Direct include dependencies include `errno.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The `sysfs(2)` API is obsolete and filesystem type ordering can vary across kernels. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs05.c

Purpose: This test case checks whether sysfs(2) system call returns appropriate error number for invalid option and for invalid filesystem name and fs index out of bounds.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`; exercises `sysfs`, `raw syscall path`; defines `verify_sysfs05`, `setup`; uses constants `EFAULT`, `EINVAL`.

Control flow centers on `verify_sysfs05`, `setup`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test` into the runner. Error-path expectations include `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is the legacy `sysfs(2)` filesystem type registry and indexes/names returned through libc or raw syscall wrappers.

Dependencies and integration points: Depends on libc or raw `sysfs(2)` wrappers and kernel support for the deprecated filesystem type query API. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The `sysfs(2)` API is obsolete and filesystem type ordering can vary across kernels. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/Makefile

Purpose: build metadata for the `sysinfo` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo01.c

Purpose: Verify that :manpage:`sysinfo(2)` succeeds to get the system information and fills the structure passed. We do sanity checks on the returned values, either comparing it againts values from /proc/ files or by checking that the values are in sane e.g. free RAM <= total RAM. Compare loads with tolerance

Important APIs/types/functions: includes `stdlib.h`, `math.h`, `sys/sysinfo.h`, `tst_test.h`; exercises `sysinfo`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is global memory, swap, process, load, and uptime counters returned in `struct sysinfo`.

Dependencies and integration points: Depends on `sysinfo(2)`, `/proc`-like global accounting consistency, and architecture-compatible `struct sysinfo` layout. Direct include dependencies include `stdlib.h`, `math.h`, `sys/sysinfo.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_EQ_LU`, `TST_EXP_LE_LU`, `TST_EXP_PASS`, `TST_KB`, `TST_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo02.c

Purpose: Verify that :manpage:sysinfo(2) returns EFAULT for an invalid address structure.

Important APIs/types/functions: includes `sys/sysinfo.h`, `tst_test.h`; exercises `sysinfo`; defines `setup`, `run`; uses constants `EFAULT`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.setup`, `.test_all` into the runner. Error-path expectations include `EFAULT`.

State and persistence behavior: Runtime state is global memory, swap, process, load, and uptime counters returned in `struct sysinfo`.

Dependencies and integration points: Depends on `sysinfo(2)`, `/proc`-like global accounting consistency, and architecture-compatible `struct sysinfo` layout. Direct include dependencies include `sys/sysinfo.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo03.c

Purpose: Test if CLOCK_BOOTTIME namespace offset is applied to sysinfo uptime and that it's consistent with /proc/uptime as well. After a call to unshare(CLONE_NEWTIME) a new timer namespace is created, the process that has called the unshare() can adjust offsets for CLOCK_MONOTONIC and CLOCK_BOOTTIME for its children by writing to the '/proc/self/timens_offsets'.

Important APIs/types/functions: includes `sys/sysinfo.h`, `lapi/posix_clocks.h`, `tst_test.h`, `lapi/sched.h`; exercises `sysinfo`, `unshare`; defines `read_proc_uptime`, `verify_sysinfo`; uses constants `CLOCK_BOOTTIME`, `CLOCK_MONOTONIC`, `CLONE_NEWTIME`.

Control flow centers on `read_proc_uptime`, `verify_sysinfo`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.needs_root`, `.needs_kconfigs`, `.tags` into the runner. Named case hints include `CONFIG_TIME_NS=y`, `linux-git`.

State and persistence behavior: Runtime state is global memory, swap, process, load, and uptime counters returned in `struct sysinfo`.

Dependencies and integration points: Depends on `sysinfo(2)`, `/proc`-like global accounting consistency, and architecture-compatible `struct sysinfo` layout. Direct include dependencies include `sys/sysinfo.h`, `lapi/posix_clocks.h`, `tst_test.h`, `lapi/sched.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syslog/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syslog/Makefile

Purpose: build metadata for the `syslog` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syslog/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog11.c

Purpose: Verify that, syslog(2) is successful for type ranging from 1 to 8 Type 0 and 1 are currently not implemented, always returns success Next two lines will clear dmesg. Uncomment if that is okay. -Robbie Williamson

Important APIs/types/functions: includes `errno.h`, `tst_test.h`, `lapi/syscalls.h`, `tst_safe_macros.h`; exercises `syslog`, `raw syscall path`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test`, `.save_restore`, `.needs_root`, `.tcnt` into the runner.

State and persistence behavior: Runtime state is the kernel log buffer and console log level, requiring privileged reads or size queries depending on the command.

Dependencies and integration points: Depends on privileged kernel log access, `klogctl`/syslog command semantics, and kernel log buffer availability. Direct include dependencies include `errno.h`, `tst_test.h`, `lapi/syscalls.h`, `tst_safe_macros.h`.

Risks and test signals: Kernel log access is security-policy-sensitive; tests may fail or skip under restricted dmesg settings. Test signals: reports through `TST_EXP_PASS`, `TST_SR_TBROK`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog12.c

Purpose: Verify that syslog(2) system call fails with appropriate error number: 1. EINVAL -- invalid type/command 2. EFAULT -- buffer outside program's accessible address space 3. EINVAL -- NULL buffer argument 4. EINVAL -- length argument set to negative value 5. EINVAL -- console level less than 0 6. EINVAL -- console level greater than 8 7. EPERM -- non-root user

Important APIs/types/functions: includes `errno.h`, `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tst_safe_macros.h`; exercises `syslog`, `raw syscall path`; defines `setup`, `setup_nonroot`, `cleanup_nonroot`, `run`; uses constants `EFAULT`, `EINVAL`, `EPERM`.

Control flow centers on `setup`, `setup_nonroot`, `cleanup_nonroot`, `run`. The `struct tst_test` registration wires `.test`, `.setup`, `.needs_root`, `.tcnt` into the runner. Error-path expectations include `EFAULT`, `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is the kernel log buffer and console log level, requiring privileged reads or size queries depending on the command.

Dependencies and integration points: Depends on privileged kernel log access, `klogctl`/syslog command semantics, and kernel log buffer availability. Direct include dependencies include `errno.h`, `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tst_safe_macros.h`.

Risks and test signals: Kernel log access is security-policy-sensitive; tests may fail or skip under restricted dmesg settings. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`, `EINVAL`, `EPERM`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tee/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tee/Makefile

Purpose: build metadata for the `tee` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tee/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee01.c

Purpose: LTP coverage for the `tee` syscall/API in this source file.

Important APIs/types/functions: includes `errno.h`, `string.h`, `signal.h`, `sys/types.h`, `tst_test.h`, `lapi/fcntl.h`, `lapi/tee.h`, `lapi/splice.h`; exercises `tee`, `read`; defines `check_file`, `tee_test`, `setup`, `cleanup`; uses constants `O_CREAT`, `O_RDONLY`, `O_TRUNC`, `O_WRONLY`.

Control flow centers on `check_file`, `tee_test`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all`, `.needs_tmpdir` into the runner.

State and persistence behavior: Runtime state is pipe buffer contents and duplicated pipe references; `tee()` copies data between pipes without consuming the input buffer.

Dependencies and integration points: Depends on pipe setup, splice/tee syscall wrappers, page-sized buffers, and non-consuming pipe duplication semantics. Direct include dependencies include `errno.h`, `string.h`, `signal.h`, `sys/types.h`, `tst_test.h`, `lapi/fcntl.h`.

Risks and test signals: Pipe buffer accounting and non-consuming semantics are subtle; false failures can come from partial writes or incorrect read ordering. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee02.c

Purpose: Verify that, tee(2) returns -1 and sets errno to: 1. EINVAL if fd_in does not refer to a pipe. 2. EINVAL if fd_out does not refer to a pipe. 3. EINVAL if fd_in and fd_out refer to the same pipe.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `tst_test.h`, `lapi/tee.h`; exercises `tee`; defines `setup`, `tee_verify`, `cleanup`; uses constants `EINVAL`, `O_CREAT`, `O_RDWR`.

Control flow centers on `setup`, `tee_verify`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt`, `.needs_tmpdir` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is pipe buffer contents and duplicated pipe references; `tee()` copies data between pipes without consuming the input buffer.

Dependencies and integration points: Depends on pipe setup, splice/tee syscall wrappers, page-sized buffers, and non-consuming pipe duplication semantics. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `tst_test.h`, `lapi/tee.h`.

Risks and test signals: Pipe buffer accounting and non-consuming semantics are subtle; false failures can come from partial writes or incorrect read ordering. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/Makefile

Purpose: build metadata for the `tgkill` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk; CFLAGS			+= -pthread`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill.h

Purpose: Shared raw-syscall wrapper for `tgkill()` tests, centralizing thread-group signal delivery through `tst_syscall(__NR_tgkill, ...)`.

Important APIs/types/functions: includes `config.h`, `lapi/syscalls.h`; defines `sys_tgkill`, `sys_gettid`; touches `raw syscall path`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is thread-group identity, per-thread signal delivery, and signal handlers used to prove `tgkill()` targets a specific task.

Dependencies and integration points: Depends on raw `tgkill` syscall wrappers, pthread/fork helpers, signal handlers, and current thread-group ids. Direct includes: `config.h`, `lapi/syscalls.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill01.c

Purpose: tgkill() delivers a signal to a specific thread. Test this by installing a SIGUSR1 handler which records the current pthread ID. Start a number of threads in parallel, then one-by-one call tgkill(..., tid, SIGUSR1) and check that the expected pthread ID was recorded. There is no standard way to map pthread -> tid, so we will have the child stash its own tid then notify the parent that the stashed tid is available.

Important APIs/types/functions: includes `pthread.h`, `stdlib.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`; exercises `tgkill`; defines `sigusr1_handler`, `start_thread`, `stop_threads`, `run`, `setup`; uses constants `SIGUSR1`.

Control flow centers on `sigusr1_handler`, `start_thread`, `stop_threads`, `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.cleanup` into the runner. Named case hints include `t:`.

State and persistence behavior: Runtime state is thread-group identity, per-thread signal delivery, and signal handlers used to prove `tgkill()` targets a specific task.

Dependencies and integration points: Depends on raw `tgkill` syscall wrappers, pthread/fork helpers, signal handlers, and current thread-group ids. Direct include dependencies include `pthread.h`, `stdlib.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`.

Risks and test signals: Signal tests are race-prone unless handler setup, target tids, and wait/join ordering are correct. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE2`, `TST_RET`, `TTERRNO`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill02.c

Purpose: tgkill() should fail with EAGAIN when RLIMIT_SIGPENDING is reached with a real-time signal. Test this by starting a child thread with SIGRTMIN blocked and a limit of 0 pending signals, then attempting to deliver SIGRTMIN from the parent thread.

Important APIs/types/functions: includes `pthread.h`, `signal.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`; exercises `tgkill`, `time`; defines `run`; uses constants `EAGAIN`, `SIGRTMIN`, `SIG_BLOCK`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner. Error-path expectations include `EAGAIN`.

State and persistence behavior: Runtime state is thread-group identity, per-thread signal delivery, and signal handlers used to prove `tgkill()` targets a specific task.

Dependencies and integration points: Depends on raw `tgkill` syscall wrappers, pthread/fork helpers, signal handlers, and current thread-group ids. Direct include dependencies include `pthread.h`, `signal.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`.

Risks and test signals: Signal tests are race-prone unless handler setup, target tids, and wait/join ordering are correct. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EAGAIN`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill03.c

Purpose: Test simple tgkill() error cases.

Important APIs/types/functions: includes `pthread.h`, `pwd.h`, `stdio.h`, `sys/types.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`; exercises `tgkill`; defines `setup`, `cleanup`, `run`; uses constants `EINVAL`, `ENOENT`, `ESRCH`, `SIGUSR1`, `SIG_BLOCK`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test` into the runner. Named case hints include `Invalid tgid`, `Invalid tid`, `Invalid signal`, `Defunct tid`, `Defunct tgid`, `Valid tgkill call`. Error-path expectations include `EINVAL`, `ENOENT`, `ESRCH`.

State and persistence behavior: Runtime state is thread-group identity, per-thread signal delivery, and signal handlers used to prove `tgkill()` targets a specific task.

Dependencies and integration points: Depends on raw `tgkill` syscall wrappers, pthread/fork helpers, signal handlers, and current thread-group ids. Direct include dependencies include `pthread.h`, `pwd.h`, `stdio.h`, `sys/types.h`, `tst_safe_pthread.h`, `tst_test.h`.

Risks and test signals: Signal tests are race-prone unless handler setup, target tids, and wait/join ordering are correct. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_ERR`, `TST_RET`, `TST_RETRY_FN_EXP_BACKOFF`, `TTERRNO`; checks errno values `EINVAL`, `ENOENT`, `ESRCH`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/time/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/time/Makefile

Purpose: build metadata for the `time` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/time/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/time/time01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/time/time01.c

Purpose: Basic test for the time(2) system call. Verify that time(2) returns the value of time in seconds since the Epoch and stores this value in the memory pointed to by the parameter.

Important APIs/types/functions: includes `time.h`, `errno.h`, `tst_test.h`; exercises `time`; defines `verify_time`.

Control flow centers on `verify_time`. The `struct tst_test` registration wires `.test`, `.tcnt` into the runner.

State and persistence behavior: Runtime state is the wall-clock seconds value returned by `time()` and optionally copied into a caller-provided pointer.

Dependencies and integration points: Depends on libc `time()` and a valid or invalid userspace pointer according to the case. Direct include dependencies include `time.h`, `errno.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/time/time01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/Makefile

Purpose: build metadata for the `timer_create` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; CPPFLAGS		+= -D_GNU_SOURCE -I$(abs_srcdir)/../include; LDLIBS			+= -lpthread -lrt; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`, plus directory-local linker flags. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create01.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> Basic test for timer_create(2): Creates a timer for each available clock using the following notification types: 1) SIGEV_NONE 2) SIGEV_SIGNAL 3) SIGEV_THREAD 4) SIGEV_THREAD_ID 5) NULL This is also regression test for commit: f18ddc13af98 ("alarmtimer: Use EOPNOTSUPP instead of ENOTSUPP")

Important APIs/types/functions: includes `signal.h`, `time.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/common_timers.h`; exercises `time`, `timer_create`, `raw syscall path`; defines `run`; uses constants `CLOCK_MONOTONIC_RAW`, `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`, `SIGALRM`, `SIGEV_NONE`, `SIGEV_SIGNAL`, `SIGEV_THREAD`, `SIGEV_THREAD_ID`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.needs_root`, `.tags` into the runner. Named case hints include `linux-git`. Error-path expectations include `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is POSIX timer objects, clocks, signal/sigevent notification setup, and kernel timer-id allocation.

Dependencies and integration points: Depends on POSIX timers, clock ids, signal/sigevent support, `timer_t` ABI, and realtime clock permissions where applicable. Direct include dependencies include `signal.h`, `time.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/common_timers.h`.

Risks and test signals: Clock support, signal delivery, and timer limits vary by kernel and libc; stale timers can leak notifications into later cases. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create02.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> Basic error handling test for timer_create(2): Passes invalid parameters when calling the syscall and checks if it fails with EFAULT/EINVAL: 1) Pass an invalid pointer for the sigevent structure parameter 2) Pass an invalid pointer for the timer ID parameter 3) Pass invalid clock type 4) Pass a sigevent with invalid sigev_notify 5) Pass a sigevent with invalid sigev_signo

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `time.h`, `signal.h`, `tst_test.h`, `lapi/common_timers.h`, `tst_safe_clocks.h`; exercises `syscall`, `time`, `timer_create`, `raw syscall path`; defines `run`, `setup`; uses constants `CLOCK_REALTIME`, `EFAULT`, `EINVAL`, `SIGALRM`, `SIGEV_NONE`, `SIGEV_SIGNAL`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup` into the runner. Error-path expectations include `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is POSIX timer objects, clocks, signal/sigevent notification setup, and kernel timer-id allocation.

Dependencies and integration points: Depends on POSIX timers, clock ids, signal/sigevent support, `timer_t` ABI, and realtime clock permissions where applicable. Direct include dependencies include `stdlib.h`, `errno.h`, `time.h`, `signal.h`, `tst_test.h`, `lapi/common_timers.h`.

Risks and test signals: Clock support, signal delivery, and timer limits vary by kernel and libc; stale timers can leak notifications into later cases. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create03.c

Purpose: Regression test for CVE-2017-18344: In kernels prior to 4.14.8 sigevent.sigev_notify is not properly verified when calling timer_create(2) with the field being set to (SIGEV_SIGNAL | SIGEV_THREAD_ID). This can be used to read arbitrary kernel memory. For more info see: https://nvd.nist.gov/vuln/detail/CVE-2017-18344 or commit: cef31d9af908 This test uses an unused number instead of SIGEV_THREAD_ID to check if this field gets verified correctly.

Important APIs/types/functions: includes `errno.h`, `signal.h`, `time.h`, `tst_test.h`, `lapi/common_timers.h`; exercises `time`, `timer_create`, `read`, `raw syscall path`; defines `run`; uses constants `CLOCK_MONOTONIC`, `EINVAL`, `SIGALRM`, `SIGEV_SIGNAL`, `SIGEV_THREAD_ID`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all`, `.tags` into the runner. Named case hints include `CVE`, `linux-git`. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is POSIX timer objects, clocks, signal/sigevent notification setup, and kernel timer-id allocation.

Dependencies and integration points: Depends on POSIX timers, clock ids, signal/sigevent support, `timer_t` ABI, and realtime clock permissions where applicable. Direct include dependencies include `errno.h`, `signal.h`, `time.h`, `tst_test.h`, `lapi/common_timers.h`.

Risks and test signals: Clock support, signal delivery, and timer limits vary by kernel and libc; stale timers can leak notifications into later cases. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/Makefile

Purpose: build metadata for the `timer_delete` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; CFLAGS			+= -D_GNU_SOURCE; CPPFLAGS		+= -I$(abs_srcdir)/../include; LDLIBS			+= -lpthread; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`, plus directory-local linker flags. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/timer_delete01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/timer_delete01.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> Basic test for timer_delete(2) Creates a timer for each available clock and then tries to delete them again. This is also regression test for commit: f18ddc13af98 ("alarmtimer: Use EOPNOTSUPP instead of ENOTSUPP")

Important APIs/types/functions: includes `errno.h`, `time.h`, `tst_test.h`, `lapi/common_timers.h`; exercises `time`, `timer_create`, `timer_delete`, `raw syscall path`; defines `run`; uses constants `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all`, `.needs_root`, `.tags` into the runner. Named case hints include `linux-git`. Error-path expectations include `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is POSIX timer lifetime; deleting a timer invalidates the `timer_t` handle and should stop future delivery.

Dependencies and integration points: Depends on POSIX timer creation/deletion and invalid handle behavior after deletion. Direct include dependencies include `errno.h`, `time.h`, `tst_test.h`, `lapi/common_timers.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/timer_delete01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/timer_delete02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/timer_delete02.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> Basic error handling test for timer_delete(2): This test case checks whether timer_delete(2) returns an appropriate error (EINVAL) for an invalid timerid parameter

Important APIs/types/functions: includes `errno.h`, `time.h`, `tst_test.h`, `lapi/common_timers.h`; exercises `time`, `timer_delete`, `raw syscall path`; defines `run`; uses constants `EINVAL`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is POSIX timer lifetime; deleting a timer invalidates the `timer_t` handle and should stop future delivery.

Dependencies and integration points: Depends on POSIX timer creation/deletion and invalid handle behavior after deletion. Direct include dependencies include `errno.h`, `time.h`, `tst_test.h`, `lapi/common_timers.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_delete/timer_delete02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/Makefile

Purpose: build metadata for the `timer_getoverrun` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/timer_getoverrun01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/timer_getoverrun01.c

Purpose: Porting from Crackerjack to LTP is done by: Manas Kumar Nayak <maknayak@in.ibm.com> This test checks base timer_getoverrun() functionality.

Important APIs/types/functions: includes `signal.h`, `time.h`, `tst_safe_clocks.h`, `lapi/syscalls.h`, `lapi/common_timers.h`; exercises `time`, `timer_create`, `timer_delete`, `timer_getoverrun`, `raw syscall path`; defines `run`; uses constants `CLOCK_REALTIME`, `EINVAL`, `SIGALRM`, `SIGEV_SIGNAL`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is POSIX timer signal overrun accounting after an interval timer expires faster than signals are consumed.

Dependencies and integration points: Depends on POSIX interval timers, signal blocking/handling, and kernel overrun accounting limits. Direct include dependencies include `signal.h`, `time.h`, `tst_safe_clocks.h`, `lapi/syscalls.h`, `lapi/common_timers.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TST_EXP_FAIL`, `TST_EXP_POSITIVE`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/timer_getoverrun01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_gettime/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_gettime/Makefile

Purpose: build metadata for the `timer_gettime` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_gettime/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_gettime/timer_gettime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_gettime/timer_gettime01.c

Purpose: Porting from Crackerjack to LTP is done by: Manas Kumar Nayak <maknayak@in.ibm.com>

Important APIs/types/functions: includes `time.h`, `signal.h`, `sys/syscall.h`, `stdio.h`, `errno.h`, `time64_variants.h`, `tst_timer.h`; exercises `syscall`, `time`, `timer_create`, `timer_gettime`, `raw syscall path`; defines `setup`, `verify`; uses constants `CLOCK_REALTIME`, `EFAULT`, `EINVAL`, `SIGALRM`, `SIGEV_SIGNAL`.

Control flow centers on `setup`, `verify`. The `struct tst_test` registration wires `.test_all`, `.test_variants`, `.setup`, `.needs_tmpdir` into the runner. Named case hints include `syscall with old kernel spec`, `syscall time64 with kernel spec`. Error-path expectations include `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is POSIX timer interval/current expiry values after creation and arming.

Dependencies and integration points: Depends on POSIX timer creation, `itimerspec` layout, and clock behavior. Direct include dependencies include `time.h`, `signal.h`, `sys/syscall.h`, `stdio.h`, `errno.h`, `time64_variants.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`, `TTERRNO`; checks errno values `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_gettime/timer_gettime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/Makefile

Purpose: build metadata for the `timer_settime` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; CFLAGS			+= -D_GNU_SOURCE; CPPFLAGS		+= -I$(abs_srcdir)/../include; LDLIBS			+= -lpthread -lrt; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`, plus directory-local linker flags. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime01.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> This tests the timer_settime(2) syscall under various conditions: 1) General initialization: No old_value, no flags 2) Setting a pointer to a itimerspec struct as old_set parameter 3) Using a periodic timer 4) Using absolute time All of these tests are supposed to be successful. This is also regression test for commit: f18ddc13af98 ("alarmtimer: Use EOPNOTSUPP instead of ENOTSUPP") e86fea764991 ("alarmtimer: Return relative times in timer_gettime") The busy loop is intentional. The signal is sent after X seconds of CPU time has been accumulated for the process and thread specific clocks.

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `time.h`, `signal.h`, `time64_variants.h`, `tst_timer.h`; exercises `syscall`, `time`, `timer_create`, `timer_delete`, `timer_gettime`, `timer_settime`, `times`, `raw syscall path`; defines `clear_signal`, `sighandler`, `setup`, `run`; uses constants `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`, `SIGALRM`.

Control flow centers on `clear_signal`, `sighandler`, `setup`, `run`. The `struct tst_test` registration wires `.test`, `.needs_root`, `.tcnt`, `.test_variants`, `.setup`, `.tags` into the runner. Named case hints include `linux-git`, `syscall with old kernel spec`, `syscall time64 with kernel spec`. Error-path expectations include `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is POSIX timer arming/disarming, absolute versus relative mode, invalid timespec validation, and signal delivery.

Dependencies and integration points: Depends on POSIX timer arming, signal notification, timespec validation, and selected clock support. Direct include dependencies include `stdlib.h`, `errno.h`, `time.h`, `signal.h`, `time64_variants.h`, `tst_timer.h`.

Risks and test signals: Timing assertions can be scheduler-sensitive, especially for short intervals or absolute time. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime02.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> This tests basic error handling of the timer_settime(2) syscall: 1) Setting pointer to new settings to NULL -> EINVAL 2) Setting tv_nsec of the itimerspec structure to a negative value -> EINVAL 3) Setting tv_nsec of the itimerspec structure to something larger than NSEC_PER_SEC -> EINVAL 4) Passing an invalid timer -> EINVAL 5) Passing an invalid address for new_value -> EFAULT 6) Passing an invalid address for old_value -> EFAULT This is also regression test for commit: f18ddc13af98 ("alarmtimer: Use EOPNOTSUPP instead of ENOTSUPP") separate description-array to (hopefully) improve readability

Important APIs/types/functions: includes `errno.h`, `time.h`, `time64_variants.h`, `tst_timer.h`; exercises `syscall`, `time`, `timer_create`, `timer_delete`, `timer_settime`, `raw syscall path`; defines `sighandler`, `setup`, `run`; uses constants `EFAULT`, `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`, `SIGALRM`.

Control flow centers on `sighandler`, `setup`, `run`. The `struct tst_test` registration wires `.test`, `.needs_root`, `.tcnt`, `.test_variants`, `.setup`, `.tags` into the runner. Named case hints include `setting new_set pointer to NULL`, `linux-git`, `syscall with old kernel spec`, `syscall time64 with kernel spec`. Error-path expectations include `EFAULT`, `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is POSIX timer arming/disarming, absolute versus relative mode, invalid timespec validation, and signal delivery.

Dependencies and integration points: Depends on POSIX timer arming, signal notification, timespec validation, and selected clock support. Direct include dependencies include `errno.h`, `time.h`, `time64_variants.h`, `tst_timer.h`.

Risks and test signals: Timing assertions can be scheduler-sensitive, especially for short intervals or absolute time. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`, `TTERRNO`; checks errno values `EFAULT`, `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime03.c

Purpose: CVE 2018-12896 Check for possible overflow of posix timer overrun counter. Create a CLOCK_REALTIME timer, set extremely low timer interval and expiration value just right to cause overrun overflow into negative values, start the timer with TIMER_ABSTIME flag to cause overruns immediately. Then just check the overrun counter in the timer signal handler. On a patched system, the value returned by timer_getoverrun() should be capped at INT_MAX and not allowed to overflow into negative range. Bug fixed in: commit 78c9c4dfbf8c04883941445a195276bb4bb92c76 Date: Tue Jun 26 15:21:32 2018 +0200 posix-timers: Sanitize overrun handling Signal handler will be called twice in total because kernel will schedule another pending signal before the timer gets disabled.

Important APIs/types/functions: includes `unistd.h`, `signal.h`, `time.h`, `limits.h`, `tst_test.h`, `tst_safe_clocks.h`; exercises `time`, `timer_getoverrun`; defines `sighandler`, `setup`, `run`, `cleanup`; uses constants `CLOCK_REALTIME`, `SIGEV_SIGNAL`, `SIGUSR1`.

Control flow centers on `sighandler`, `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.tags` into the runner. Named case hints include `linux-git`, `CVE`.

State and persistence behavior: Runtime state is POSIX timer arming/disarming, absolute versus relative mode, invalid timespec validation, and signal delivery.

Dependencies and integration points: Depends on POSIX timer arming, signal notification, timespec validation, and selected clock support. Direct include dependencies include `unistd.h`, `signal.h`, `time.h`, `limits.h`, `tst_test.h`, `tst_safe_clocks.h`.

Risks and test signals: Timing assertions can be scheduler-sensitive, especially for short intervals or absolute time. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/Makefile

Purpose: build metadata for the `timerfd` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; LDLIBS			+= -lrt; timerfd_settime02:	LDLIBS	+= -pthread; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`, plus directory-local linker flags. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd01.c

Purpose: timerfd() test by Davide Libenzi (test app for timerfd) Davide Libenzi <davidel@xmailserver.org> Description: Test timerfd with the flags: 1) CLOCK_MONOTONIC 2) CLOCK_REALTIME HISTORY 28/05/2008 Initial contribution by Davide Libenzi <davidel@xmailserver.org> 28/05/2008 Integrated to LTP by Subrata Modak <subrata@linux.vnet.ibm.com>

Important APIs/types/functions: includes `poll.h`, `time64_variants.h`, `tst_timer.h`, `tst_safe_timerfd.h`; exercises `syscall`, `timerfd_gettime`, `timerfd_settime`, `read`; defines `settime`, `waittmr`, `run`, `setup`; uses constants `CLOCK_MONOTONIC`, `CLOCK_REALTIME`, `EAGAIN`, `O_NONBLOCK`, `TFD_TIMER_ABSTIME`.

Control flow centers on `settime`, `waittmr`, `run`, `setup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.test_variants`, `.setup` into the runner. Named case hints include `syscall with old kernel spec`, `syscall time64 with kernel spec`. Error-path expectations include `EAGAIN`.

State and persistence behavior: Runtime state is timer file descriptors, expiration counters read from them, clock ids, flags, and `timerfd_settime()`/`gettime()` state.

Dependencies and integration points: Depends on `timerfd_create/gettime/settime`, raw syscall wrappers, clock ids, read semantics for expiration counters, and kernel support for newer flags. Direct include dependencies include `poll.h`, `time64_variants.h`, `tst_timer.h`, `tst_safe_timerfd.h`.

Risks and test signals: Timerfd tests are sensitive to clock availability, blocking reads, and exact expiration counts under scheduler delay. Test signals: reports through `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`, `TTERRNO`; checks errno values `EAGAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd02.c

Purpose: This test verifies that: - TFD_CLOEXEC sets the close-on-exec file status flag on the new open file - TFD_NONBLOCK sets the O_NONBLOCK file status flag on the new open file

Important APIs/types/functions: includes `tst_test.h`, `tst_safe_timerfd.h`, `lapi/fcntl.h`, `lapi/syscalls.h`; exercises `open`, `close`; defines `run`, `cleanup`; uses constants `CLOCK_REALTIME`, `O_NONBLOCK`, `TFD_CLOEXEC`, `TFD_NONBLOCK`.

Control flow centers on `run`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is timer file descriptors, expiration counters read from them, clock ids, flags, and `timerfd_settime()`/`gettime()` state.

Dependencies and integration points: Depends on `timerfd_create/gettime/settime`, raw syscall wrappers, clock ids, read semantics for expiration counters, and kernel support for newer flags. Direct include dependencies include `tst_test.h`, `tst_safe_timerfd.h`, `lapi/fcntl.h`, `lapi/syscalls.h`.

Risks and test signals: Timerfd tests are sensitive to clock availability, blocking reads, and exact expiration counts under scheduler delay. Test signals: reports through `TST_EXP_EQ_LI`, `TST_EXP_FD`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd04.c

Purpose: Test that timerfd adds correctly an offset with absolute expiration time. After a call to unshare(CLONE_NEWTIME) a new timer namespace is created, the process that has called the unshare() can adjust offsets for CLOCK_MONOTONIC and CLOCK_BOOTTIME for its children by writing to the '/proc/self/timens_offsets'.

Important APIs/types/functions: includes `stdlib.h`, `time64_variants.h`, `tst_safe_clocks.h`, `tst_safe_timerfd.h`, `tst_timer.h`, `lapi/sched.h`; exercises `syscall`, `time`, `timerfd_settime`, `unshare`; defines `setup`, `verify_timerfd`; uses constants `CLOCK_BOOTTIME`, `CLOCK_MONOTONIC`, `CLONE_NEWTIME`, `TFD_TIMER_ABSTIME`.

Control flow centers on `setup`, `verify_timerfd`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.test_variants`, `.setup`, `.needs_root`, `.needs_kconfigs` into the runner. Named case hints include `CONFIG_TIME_NS=y`, `syscall with old kernel spec`, `syscall time64 with kernel spec`.

State and persistence behavior: Runtime state is timer file descriptors, expiration counters read from them, clock ids, flags, and `timerfd_settime()`/`gettime()` state.

Dependencies and integration points: Depends on `timerfd_create/gettime/settime`, raw syscall wrappers, clock ids, read semantics for expiration counters, and kernel support for newer flags. Direct include dependencies include `stdlib.h`, `time64_variants.h`, `tst_safe_clocks.h`, `tst_safe_timerfd.h`, `tst_timer.h`, `lapi/sched.h`.

Risks and test signals: Timerfd tests are sensitive to clock availability, blocking reads, and exact expiration counts under scheduler delay. Test signals: reports through `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_create01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_create01.c

Purpose: Zeng Linggang <zenglg.jy@cn.fujitsu.com> This test verifies that: - clockid argument is neither CLOCK_MONOTONIC nor CLOCK_REALTIME, EINVAL would return. - flags is invalid, EINVAL would return.

Important APIs/types/functions: includes `errno.h`, `tst_test.h`, `tst_safe_timerfd.h`; exercises `timerfd_create`; defines `run`; uses constants `CLOCK_MONOTONIC`, `CLOCK_REALTIME`, `EINVAL`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test`, `.tcnt` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is timer file descriptors, expiration counters read from them, clock ids, flags, and `timerfd_settime()`/`gettime()` state.

Dependencies and integration points: Depends on `timerfd_create/gettime/settime`, raw syscall wrappers, clock ids, read semantics for expiration counters, and kernel support for newer flags. Direct include dependencies include `errno.h`, `tst_test.h`, `tst_safe_timerfd.h`.

Risks and test signals: Timerfd tests are sensitive to clock availability, blocking reads, and exact expiration counts under scheduler delay. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_create01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_gettime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_gettime01.c

Purpose: DESCRIPTION Verify that, 1. fd is not a valid file descriptor, EBADF would return. 2. curr_value is not valid a pointer, EFAULT would return. 3. fd is not a valid timerfd file descriptor, EINVAL would return.

Important APIs/types/functions: includes `time64_variants.h`, `tst_timer.h`, `tst_safe_timerfd.h`; exercises `syscall`, `timerfd_create`, `timerfd_gettime`, `close`; defines `setup`, `cleanup`, `run`; uses constants `CLOCK_REALTIME`, `EBADF`, `EFAULT`, `EINVAL`, `O_CREAT`, `O_RDWR`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.test_variants`, `.setup`, `.cleanup`, `.needs_tmpdir` into the runner. Named case hints include `syscall with old kernel spec`, `syscall time64 with kernel spec`. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is timer file descriptors, expiration counters read from them, clock ids, flags, and `timerfd_settime()`/`gettime()` state.

Dependencies and integration points: Depends on `timerfd_create/gettime/settime`, raw syscall wrappers, clock ids, read semantics for expiration counters, and kernel support for newer flags. Direct include dependencies include `time64_variants.h`, `tst_timer.h`, `tst_safe_timerfd.h`.

Risks and test signals: Timerfd tests are sensitive to clock availability, blocking reads, and exact expiration counts under scheduler delay. Test signals: reports through `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_gettime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_settime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_settime01.c

Purpose: DESCRIPTION Verify that, 1. fd is not a valid file descriptor, EBADF would return. 2. old_value is not valid a pointer, EFAULT would return. 3. fd is not a valid timerfd file descriptor, EINVAL would return. 4. flags is invalid, EINVAL would return.

Important APIs/types/functions: includes `time64_variants.h`, `tst_timer.h`, `lapi/timerfd.h`; exercises `syscall`, `timerfd_create`, `timerfd_settime`, `close`; defines `setup`, `cleanup`, `run`; uses constants `CLOCK_REALTIME`, `EBADF`, `EFAULT`, `EINVAL`, `O_CREAT`, `O_RDWR`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.test_variants`, `.setup`, `.cleanup`, `.needs_tmpdir` into the runner. Named case hints include `syscall with old kernel spec`, `syscall time64 with kernel spec`. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is timer file descriptors, expiration counters read from them, clock ids, flags, and `timerfd_settime()`/`gettime()` state.

Dependencies and integration points: Depends on `timerfd_create/gettime/settime`, raw syscall wrappers, clock ids, read semantics for expiration counters, and kernel support for newer flags. Direct include dependencies include `time64_variants.h`, `tst_timer.h`, `lapi/timerfd.h`.

Risks and test signals: Timerfd tests are sensitive to clock availability, blocking reads, and exact expiration counts under scheduler delay. Test signals: reports through `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_settime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_settime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_settime02.c

Purpose: CVE-2017-10661 Test for race condition vulnerability in timerfd_settime(). Multiple concurrent calls of timerfd_settime() clearing the CANCEL_ON_SET flag may cause memory corruption. Fixed in: commit 1e38da300e1e395a15048b0af1e5305bd91402f6 Date: Tue Jan 31 15:24:03 2017 +0100 timerfd: Protect the might cancel mechanism proper

Important APIs/types/functions: includes `unistd.h`, `time64_variants.h`, `tst_timer.h`, `tst_safe_timerfd.h`, `tst_fuzzy_sync.h`; exercises `syscall`, `timerfd_settime`; defines `setup`, `cleanup`, `punch_clock`, `run`; uses constants `CLOCK_REALTIME`, `TFD_TIMER_ABSTIME`, `TFD_TIMER_CANCEL_ON_SET`.

Control flow centers on `setup`, `cleanup`, `punch_clock`, `run`. The `struct tst_test` registration wires `.test_all`, `.test_variants`, `.setup`, `.cleanup`, `.tags` into the runner. Named case hints include `linux-git`, `CVE`, `syscall with old kernel spec`, `syscall time64 with kernel spec`.

State and persistence behavior: Runtime state is timer file descriptors, expiration counters read from them, clock ids, flags, and `timerfd_settime()`/`gettime()` state.

Dependencies and integration points: Depends on `timerfd_create/gettime/settime`, raw syscall wrappers, clock ids, read semantics for expiration counters, and kernel support for newer flags. Direct include dependencies include `unistd.h`, `time64_variants.h`, `tst_timer.h`, `tst_safe_timerfd.h`, `tst_fuzzy_sync.h`.

Risks and test signals: Timerfd tests are sensitive to clock availability, blocking reads, and exact expiration counts under scheduler delay. Test signals: reports through `TBROK`, `TFAIL`, `TINFO`, `TPASS`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`, `TST_TAINT_D`, `TST_TAINT_W`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd_settime02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/times/Makefile

Purpose: build metadata for the `times` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/times01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/times/times01.c

Purpose: This is a Phase I test for the times(2) system call. It is intended to provide a limited exposure of the system call.

Important APIs/types/functions: includes `sys/times.h`, `errno.h`, `tst_test.h`; exercises `times`; defines `verify_times`.

Control flow centers on `verify_times`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is per-process CPU tick accounting in `struct tms` plus monotonic elapsed clock ticks.

Dependencies and integration points: Depends on `times(2)`, `sysconf(_SC_CLK_TCK)`, and stable CPU accounting around busy or elapsed work. Direct include dependencies include `sys/times.h`, `errno.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/times01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/times03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/times/times03.c

Purpose: DESCRIPTION Testcase to check the basic functionality of the times() system call. ALGORITHM This testcase checks the values that times(2) system call returns. Start a process, and spend some CPU time by performing a spin in a for-loop. Then use the times() system call, to determine the cpu time/sleep time, and other statistics. 07/2001 John George At least some CPU time must be used in system space. This is achieved by executing the times(2) call for at least 2 secs. This logic makes it independent of the processor speed. Run the test in a child to reset times in case of -i option.

Important APIs/types/functions: includes `sys/types.h`, `sys/times.h`, `errno.h`, `sys/wait.h`, `time.h`, `signal.h`, `stdlib.h`, `tst_test.h`; exercises `time`, `times`; defines `sighandler`, `work`, `generate_utime`, `generate_stime`, `verify_times`, `do_test`, `setup`; uses constants `SIGALRM`.

Control flow centers on `sighandler`, `work`, `generate_utime`, `generate_stime`, `verify_times`, `do_test`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all` into the runner.

State and persistence behavior: Runtime state is per-process CPU tick accounting in `struct tms` plus monotonic elapsed clock ticks.

Dependencies and integration points: Depends on `times(2)`, `sysconf(_SC_CLK_TCK)`, and stable CPU accounting around busy or elapsed work. Direct include dependencies include `sys/types.h`, `sys/times.h`, `errno.h`, `sys/wait.h`, `time.h`, `signal.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/times03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tkill/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tkill/Makefile

Purpose: build metadata for the `tkill` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tkill/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tkill/tkill01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tkill/tkill01.c

Purpose: Ported from Crackerjack to LTP by Manas Kumar Nayak maknayak@in.ibm.com> Basic tests for the tkill syscall. [Algorithm] Calls tkill and capture signal to verify success.

Important APIs/types/functions: includes `signal.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `syscall`, `tkill`, `raw syscall path`; defines `sighandler`, `setup`, `run`; uses constants `SIGUSR1`.

Control flow centers on `sighandler`, `setup`, `run`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.test_all` into the runner.

State and persistence behavior: Runtime state is task ids and signal delivery to a specific thread/task, including invalid pid/signal paths.

Dependencies and integration points: Depends on raw `tkill` syscall wrappers, process/thread ids, signal handlers, and invalid signal/pid error behavior. Direct include dependencies include `signal.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tkill/tkill01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tkill/tkill02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tkill/tkill02.c

Purpose: Ported from Crackerjack to LTP by Manas Kumar Nayak maknayak@in.ibm.com> Basic tests for the tkill() errors. [Algorithm] - EINVAL on an invalid thread ID - ESRCH when no process with the specified thread ID exists

Important APIs/types/functions: includes `stdio.h`, `stdlib.h`, `errno.h`, `unistd.h`, `signal.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `tkill`, `raw syscall path`; defines `setup`, `run`; uses constants `EINVAL`, `ESRCH`, `SIGUSR1`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.needs_tmpdir`, `.setup`, `.test` into the runner. Error-path expectations include `EINVAL`, `ESRCH`.

State and persistence behavior: Runtime state is task ids and signal delivery to a specific thread/task, including invalid pid/signal paths.

Dependencies and integration points: Depends on raw `tkill` syscall wrappers, process/thread ids, signal handlers, and invalid signal/pid error behavior. Direct include dependencies include `stdio.h`, `stdlib.h`, `errno.h`, `unistd.h`, `signal.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EINVAL`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tkill/tkill02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/truncate/Makefile

Purpose: build metadata for the `truncate` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`, plus `../utils/newer_64.mk` for 64-bit variants. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate02.c

Purpose: 07/2001 John George Verify that: - truncate(2) truncates a file to a specified length successfully. - If the file is larger than the specified length, the extra data is lost. - If the file is shorter than the specified length, the extra data is filled by '0'. - truncate(2) doesn't change offset.

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `sys/types.h`, `sys/stat.h`, `string.h`, `tst_test.h`, `tst_safe_prw.h`; exercises `truncate`; defines `verify_truncate`, `setup`, `cleanup`; uses constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_truncate`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.tcnt`, `.test` into the runner.

State and persistence behavior: Runtime state is regular file content, length, descriptor offsets, permissions, symlink loops, resource limits, and filesystem error paths.

Dependencies and integration points: Depends on temporary filesystem fixtures, `truncate(2)`, resource limits, bad-address helpers, credential switching, and filesystem-specific error behavior. Direct include dependencies include `errno.h`, `unistd.h`, `sys/types.h`, `sys/stat.h`, `string.h`, `tst_test.h`.

Risks and test signals: Filesystem permissions, RLIMIT_FSIZE, symlink-loop limits, and bad-address checks vary; setup must isolate each errno path. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate03.c

Purpose: 07/2001 John George Verify that: - truncate(2) returns -1 and sets errno to EACCES if search/write permission denied for the process on the component of the path prefix or named file. - truncate(2) returns -1 and sets errno to ENOTDIR if the component of the path prefix is not a directory. - truncate(2) returns -1 and sets errno to EFAULT if pathname points outside user's accessible address space. - truncate(2) returns -1 and sets errno to ENAMETOOLONG if the component of a pathname exceeded 255 characters or entire pathname exceeds 1023 characters. - truncate(2) returns -1 and sets errno to ENOENT if the named file does not exist. - truncate(2) returns -1 and sets errno to EISDIR if the named file is a directory. - truncate(2) returns -1 and sets errno to EFBIG if the argument length is larger than the maximum file size. - truncate(2) re

Important APIs/types/functions: includes `stdio.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/mman.h`, `errno.h`, `string.h`, `signal.h`; exercises `truncate`, `write`; defines `setup`, `verify_truncate`; uses constants `EACCES`, `EFAULT`, `EFBIG`, `EISDIR`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `SIGXFSZ`, `SIG_BLOCK`.

Control flow centers on `setup`, `verify_truncate`. The `struct tst_test` registration wires `.needs_root`, `.needs_tmpdir`, `.setup`, `.tcnt`, `.test` into the runner. Error-path expectations include `EACCES`, `EFAULT`, `EFBIG`, `EISDIR`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is regular file content, length, descriptor offsets, permissions, symlink loops, resource limits, and filesystem error paths.

Dependencies and integration points: Depends on temporary filesystem fixtures, `truncate(2)`, resource limits, bad-address helpers, credential switching, and filesystem-specific error behavior. Direct include dependencies include `stdio.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/mman.h`, `errno.h`.

Risks and test signals: Filesystem permissions, RLIMIT_FSIZE, symlink-loop limits, and bad-address checks vary; setup must isolate each errno path. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EACCES`, `EFAULT`, `EFBIG`, `EISDIR`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/Makefile

Purpose: build metadata for the `ulimit` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/ulimit01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/ulimit01.c

Purpose: Tests the basic functionality of :manpage:`ulimit(3)` with UL_GETFSIZE and UL_SETFSIZE.

Important APIs/types/functions: includes `ulimit.h`, `tst_test.h`; exercises `ulimit`; defines `run`; uses constants `UL_GETFSIZE`, `UL_SETFSIZE`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is the process file-size limit manipulated through the legacy libc `ulimit()` interface.

Dependencies and integration points: Depends on libc `ulimit()` and process resource limit state. Direct include dependencies include `ulimit.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_POSITIVE`, `TST_PASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/ulimit01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umask/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umask/Makefile

Purpose: build metadata for the `umask` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umask/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umask/umask01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umask/umask01.c

Purpose: 07/2001 Ported by John George umask(2) sets the mask from 0000 to 0777 while we create files, the previous value of the mask should be returned correctly, and the file mode should be correct for each creation mask.

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `sys/types.h`, `sys/stat.h`, `tst_test.h`; exercises `umask`; defines `verify_umask`.

Control flow centers on `verify_umask`. The `struct tst_test` registration wires `.test_all`, `.needs_tmpdir` into the runner.

State and persistence behavior: Runtime state is the process file creation mask and resulting modes of newly created files.

Dependencies and integration points: Depends on process umask state, file creation helpers, and stat-visible permission bits. Direct include dependencies include `errno.h`, `stdio.h`, `sys/types.h`, `sys/stat.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umask/umask01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount/Makefile

Purpose: build metadata for the `umount` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; INSTALL_TARGETS		:= test_umount; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount01.c

Purpose: Check the basic functionality of the :manpage:`umount(2)` system call.

Important APIs/types/functions: includes `sys/mount.h`, `tst_test.h`; exercises `umount`, `mount`; defines `verify_umount`, `setup`, `cleanup`; uses constants `EBUSY`.

Control flow centers on `verify_umount`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.setup`, `.cleanup`, `.test_all` into the runner. Error-path expectations include `EBUSY`.

State and persistence behavior: Runtime state is mounted test filesystems, busy file descriptors, path validity, privileges, and cleanup unmount attempts.

Dependencies and integration points: Depends on root privileges, mount helpers, temporary mountpoints, busy file descriptors, and path/error fixtures. Direct include dependencies include `sys/mount.h`, `tst_test.h`.

Risks and test signals: Unmount tests can leave mounted fixtures on failure; busy-mount cases must close descriptors before cleanup. Test signals: reports through `TINFO`, `TST_ERR`, `TST_EXP_PASS`, `TST_RET`; checks errno values `EBUSY`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount02.c

Purpose: Check for basic errors returned by :manpage:`umount(2)` system call. Verify that :manpage:`umount(2)` returns -1 and sets errno to 1. EBUSY if it cannot be umounted, because dir is still busy. 2. EFAULT if specialfile or device file points to invalid address space. 3. ENOENT if pathname was empty or has a nonexistent component. 4. EINVAL if specialfile or device is invalid or not a mount point. 5. ENAMETOOLONG if pathname was longer than MAXPATHLEN.

Important APIs/types/functions: includes `sys/mount.h`, `tst_test.h`; exercises `umount`, `mount`; defines `verify_umount`, `setup`, `cleanup`; uses constants `EBUSY`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`.

Control flow centers on `verify_umount`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.needs_root`, `.setup`, `.cleanup`, `.test` into the runner. Named case hints include `Already mounted/busy`, `Invalid address`, `Directory not found`, `Invalid  device`, `Pathname too long`. Error-path expectations include `EBUSY`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`.

State and persistence behavior: Runtime state is mounted test filesystems, busy file descriptors, path validity, privileges, and cleanup unmount attempts.

Dependencies and integration points: Depends on root privileges, mount helpers, temporary mountpoints, busy file descriptors, and path/error fixtures. Direct include dependencies include `sys/mount.h`, `tst_test.h`.

Risks and test signals: Unmount tests can leave mounted fixtures on failure; busy-mount cases must close descriptors before cleanup. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EBUSY`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount03.c

Purpose: Verify that :manpage:`umount(2)` returns -1 and sets errno to EPERM if the user is not the super-user.

Important APIs/types/functions: includes `pwd.h`, `sys/mount.h`, `tst_test.h`; exercises `umount`, `mount`; defines `verify_umount`, `setup`, `cleanup`; uses constants `EPERM`.

Control flow centers on `verify_umount`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.setup`, `.cleanup`, `.test_all` into the runner. Error-path expectations include `EPERM`.

State and persistence behavior: Runtime state is mounted test filesystems, busy file descriptors, path validity, privileges, and cleanup unmount attempts.

Dependencies and integration points: Depends on root privileges, mount helpers, temporary mountpoints, busy file descriptors, and path/error fixtures. Direct include dependencies include `pwd.h`, `sys/mount.h`, `tst_test.h`.

Risks and test signals: Unmount tests can leave mounted fixtures on failure; busy-mount cases must close descriptors before cleanup. Test signals: reports through `TERRNO`, `TST_EXP_FAIL`; checks errno values `EPERM`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount2/Makefile

Purpose: build metadata for the `umount2` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_01.c

Purpose: This program is distributed in the hope that it would be useful, but alone with this program. DESCRIPTION Test for feature MNT_DETACH of umount2(). "Perform a lazy unmount: make the mount point unavailable for new accesses, and actually perform the unmount when the mount point ceases to be busy." check the unavailability for new access check the old fd still points to the file in previous mount point and is available

Important APIs/types/functions: includes `errno.h`, `test.h`, `tso_safe_macros.h`, `lapi/mount.h`; exercises `umount`, `umount2`, `mount`, `close`; defines `setup`, `umount2_verify`, `cleanup`, `main`; uses constants `EXIT`, `MNT_DETACH`, `O_RDONLY`.

Control flow centers on `setup`, `umount2_verify`, `cleanup`, `main`. This is an older harness test using `tst_parse_opts()`, `TEST_LOOPING()`, and explicit cleanup. Error-path expectations include `EXIT`.

State and persistence behavior: Runtime state is mounted filesystems plus `umount2()` flags such as forced, lazy, expire, and no-follow behavior.

Dependencies and integration points: Depends on raw `umount2()` or libc wrapper, mount helpers, device acquisition in legacy tests, and flag-specific kernel semantics. Direct include dependencies include `errno.h`, `test.h`, `tso_safe_macros.h`, `lapi/mount.h`.

Risks and test signals: Flag combinations have special kernel behavior and legacy device handling can leave mounted filesystems if cleanup is incomplete. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_TOTAL`, `TTERRNO`; checks errno values `EXIT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_02.c

Purpose: Test for feature MNT_EXPIRE of :manpage:`umount2(2)`: - EINVAL when flag is specified with either MNT_FORCE or MNT_DETACH - EAGAIN when initial call to :manpage:`umount2(2)` with MNT_EXPIRE - EAGAIN when :manpage:`umount2(2)` with MNT_EXPIRE after :manpage:`access(2)` - succeed when second call to :manpage:`umount2(2)` with MNT_EXPIRE Test for feature UMOUNT_NOFOLLOW of :manpage:`umount2(2)`: - EINVAL when target is a symbolic link - succeed when target is a mount point

Important APIs/types/functions: includes `lapi/mount.h`, `tst_test.h`; exercises `symlink`, `umount`, `umount2`, `mount`; defines `umount2_retry`, `test_umount2`, `setup`, `cleanup`; uses constants `EAGAIN`, `EBUSY`, `EINVAL`, `MNT_DETACH`, `MNT_EXPIRE`, `MNT_FORCE`, `UMOUNT_NOFOLLOW`.

Control flow centers on `umount2_retry`, `test_umount2`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.cleanup`, `.setup`, `.needs_root`, `.mntpoint`, `.test` into the runner. Named case hints include `umount2(`. Error-path expectations include `EAGAIN`, `EBUSY`, `EINVAL`.

State and persistence behavior: Runtime state is mounted filesystems plus `umount2()` flags such as forced, lazy, expire, and no-follow behavior.

Dependencies and integration points: Depends on raw `umount2()` or libc wrapper, mount helpers, device acquisition in legacy tests, and flag-specific kernel semantics. Direct include dependencies include `lapi/mount.h`, `tst_test.h`.

Risks and test signals: Flag combinations have special kernel behavior and legacy device handling can leave mounted filesystems if cleanup is incomplete. Test signals: reports through `TINFO`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `TST_PASS`; checks errno values `EAGAIN`, `EBUSY`, `EINVAL`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/uname/Makefile

Purpose: build metadata for the `uname` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; uname04:	CFLAGS += -D_GNU_SOURCE; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname01.c

Purpose: Basic test for uname(2): Calling uname() succeeded and got correct sysname.

Important APIs/types/functions: includes `sys/utsname.h`, `errno.h`, `string.h`, `tst_test.h`; exercises `uname`; defines `verify_uname`.

Control flow centers on `verify_uname`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is kernel utsname data and architecture/personality-dependent field length handling.

Dependencies and integration points: Depends on libc `uname()`, personality flags for old-uts behavior, and bad-address helpers for EFAULT coverage. Direct include dependencies include `sys/utsname.h`, `errno.h`, `string.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_PASS`, `TST_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname02.c

Purpose: Basic test for uname(): Calling uname() with invalid buf got EFAULT.

Important APIs/types/functions: includes `errno.h`, `sys/utsname.h`, `tst_test.h`; exercises `uname`; defines `verify_uname`, `setup`; uses constants `EFAULT`.

Control flow centers on `verify_uname`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup` into the runner. Error-path expectations include `EFAULT`.

State and persistence behavior: Runtime state is kernel utsname data and architecture/personality-dependent field length handling.

Dependencies and integration points: Depends on libc `uname()`, personality flags for old-uts behavior, and bad-address helpers for EFAULT coverage. Direct include dependencies include `errno.h`, `sys/utsname.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname04.c

Purpose: Check that memory after the string terminator in all the utsname fields has been zeroed. cve-2012-0957 leaked kernel memory through the release field when the UNAME26 personality was set. Thanks to Kees Cook for the original proof of concept: http://www.securityfocus.com/bid/55855/info

Important APIs/types/functions: includes `string.h`, `sys/utsname.h`, `tst_test.h`, `lapi/personality.h`; exercises `uname`; defines `check_field`, `try_leak_bytes`, `run`.

Control flow centers on `check_field`, `try_leak_bytes`, `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.tags` into the runner. Named case hints include `CVE`.

State and persistence behavior: Runtime state is kernel utsname data and architecture/personality-dependent field length handling.

Dependencies and integration points: Depends on libc `uname()`, personality flags for old-uts behavior, and bad-address helpers for EFAULT coverage. Direct include dependencies include `string.h`, `sys/utsname.h`, `tst_test.h`, `lapi/personality.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/Makefile

Purpose: build metadata for the `unlink` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink05.c

Purpose: Test the basic functionality of :manpage:`unlink(2)`: - :manpage:`unlink(2)` can delete regular file successfully - :manpage:`unlink(2)` can delete fifo file successfully

Important APIs/types/functions: includes `errno.h`, `sys/types.h`, `unistd.h`, `stdio.h`, `tst_test.h`; exercises `unlink`; defines `file_create`, `fifo_create`, `verify_unlink`.

Control flow centers on `file_create`, `fifo_create`, `verify_unlink`. The `struct tst_test` registration wires `.needs_tmpdir`, `.tcnt`, `.test` into the runner.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `errno.h`, `sys/types.h`, `unistd.h`, `stdio.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink07.c

Purpose: Verify that :manpage:`unlink(2)`: fails with: - ENOENT when file does not exist - ENOENT when pathname is empty - ENOENT when a component in pathname does not exist - EFAULT when pathname points outside the accessible address space - ENOTDIR when a component used as a directory in pathname is not, in fact, a directory - ENAMETOOLONG when pathname is too long

Important APIs/types/functions: includes `errno.h`, `limits.h`, `string.h`, `unistd.h`, `tst_test.h`; exercises `unlink`; defines `verify_unlink`, `setup`; uses constants `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

Control flow centers on `verify_unlink`, `setup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.tcnt`, `.test` into the runner. Named case hints include `nonexistfile`, `nefile/file`, `file/file`. Error-path expectations include `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `errno.h`, `limits.h`, `string.h`, `unistd.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink08.c

Purpose: Verify that :manpage:`unlink(2)`: fails with: - EACCES when no write access to the directory containing pathname - EACCES when one of the directories in pathname did not allow search - EISDIR when deleting directory as root user - EISDIR when deleting directory as non-root user

Important APIs/types/functions: includes `errno.h`, `pwd.h`, `stdlib.h`, `unistd.h`, `tst_test.h`; exercises `unlink`, `write`; defines `verify_unlink`, `do_unlink`, `setup`; uses constants `EACCES`, `EISDIR`.

Control flow centers on `verify_unlink`, `do_unlink`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.needs_tmpdir`, `.setup`, `.tcnt`, `.test` into the runner. Named case hints include `unwrite_dir/file`, `unsearch_dir/file`, `regdir`. Error-path expectations include `EACCES`, `EISDIR`.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `errno.h`, `pwd.h`, `stdlib.h`, `unistd.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EACCES`, `EISDIR`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink09.c

Purpose: Verify that :manpage:`unlink(2)`: fails with EPERM when target file is marked as immutable or append-only. inode attributes in tmpfs are supported from kernel 6.0 https://lore.kernel.org/all/20220715015912.2560575-1-tytso@mit.edu/ If unlink() succeeded unexpectedly, test file should be restored.

Important APIs/types/functions: includes `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`; exercises `unlink`, `ioctl`; defines `setup_inode_flag`, `setup`, `cleanup`, `verify_unlink`; uses constants `ENOTTY`, `EPERM`, `FS_APPEND_FL`, `FS_IMMUTABLE_FL`, `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`.

Control flow centers on `setup_inode_flag`, `setup`, `cleanup`, `verify_unlink`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.cleanup`, `.test`, `.mntpoint`, `.needs_root`, `.mount_device`, `.all_filesystems`, `.skip_filesystems` into the runner. Named case hints include `fuse`. Error-path expectations include `ENOTTY`, `EPERM`.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TST_ERR`, `TST_EXP_FAIL`, `TST_RET`; checks errno values `ENOTTY`, `EPERM`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink10.c

Purpose: Verify that :manpage:`unlink(2)`: fails with EROFS when target file is on a read-only filesystem.

Important APIs/types/functions: includes `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`; exercises `unlink`, `ioctl`, `read`; defines `run`; uses constants `EROFS`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all`, `.needs_root`, `.mntpoint` into the runner. Error-path expectations include `EROFS`.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EROFS`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/Makefile

Purpose: build metadata for the `unlinkat` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/unlinkat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/unlinkat01.c

Purpose: Basic :manpage:`unlinkat(2)` test. tesfile2 will be unlinked by test0. testfile3 will be unlined by test1.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`, `tst_safe_stdio.h`, `lapi/fcntl.h`; exercises `unlinkat`; defines `getfd`, `run`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `AT_REMOVEDIR`, `EBADF`, `EINVAL`, `ENOTDIR`, `O_CREAT`, `O_DIRECTORY`, `O_RDWR`.

Control flow centers on `getfd`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.tcnt`, `.setup`, `.test`, `.cleanup` into the runner. Error-path expectations include `EBADF`, `EINVAL`, `ENOTDIR`.

State and persistence behavior: Runtime state is directory file descriptors, cwd-relative paths, flags, and directory/file removal fixtures.

Dependencies and integration points: Depends on directory fd setup, path construction, `unlinkat()` flags, and temporary directory cleanup. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`, `tst_safe_stdio.h`, `lapi/fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TTERRNO`; checks errno values `EBADF`, `EINVAL`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/unlinkat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/Makefile

Purpose: build metadata for the `unshare` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare01.c

Purpose: Ported from Crackerjack to LTP by Manas Kumar Nayak maknayak@in.ibm.com> Basic tests for the :manpage:`unshare(2)` syscall. [Algorithm] Calls :manpage:`unshare(2)` for different CLONE_* flags in a child process and expects them to succeed.

Important APIs/types/functions: includes `stdio.h`, `sys/wait.h`, `sys/types.h`, `sys/param.h`, `sys/syscall.h`, `sched.h`, `limits.h`, `unistd.h`; exercises `syscall`, `unshare`; defines `run`; uses constants `CLONE_`, `CLONE_FILES`, `CLONE_FS`, `CLONE_NEWNS`.

Control flow centers on `run`. The `struct tst_test` registration wires `.tcnt`, `.needs_tmpdir`, `.needs_root`, `.test` into the runner.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `stdio.h`, `sys/wait.h`, `sys/types.h`, `sys/param.h`, `sys/syscall.h`, `sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TST_EXP_PASS`, `TST_TEST_TCONF`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare02.c

Purpose: Ported from Crackerjack to LTP by Manas Kumar Nayak maknayak@in.ibm.com> Basic tests for the :manpage:`unshare(2)` errors. - EINVAL on invalid flags - EPERM when process is missing required privileges

Important APIs/types/functions: includes `stdio.h`, `sys/wait.h`, `sys/types.h`, `sys/param.h`, `sys/syscall.h`, `sched.h`, `limits.h`, `unistd.h`; exercises `syscall`, `unshare`; defines `run`, `setup`; uses constants `CLONE_NEWNS`, `EINVAL`, `EPERM`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.tcnt`, `.needs_tmpdir`, `.needs_root`, `.setup`, `.test` into the runner. Error-path expectations include `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `stdio.h`, `sys/wait.h`, `sys/types.h`, `sys/param.h`, `sys/syscall.h`, `sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TST_EXP_FAIL`, `TST_TEST_TCONF`; checks errno values `EINVAL`, `EPERM`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare03.c

Purpose: This test case based on kernel self-test unshare_test.c to check that the kernel handles the EMFILE error when a parent process changes file descriptor limits and the child process tries to unshare (CLONE_FILES).

Important APIs/types/functions: includes `tst_test.h`, `config.h`, `lapi/sched.h`; exercises `syscall`, `unshare`; defines `run`, `setup`; uses constants `CLONE_FILES`, `SIGCHLD`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.test_all`, `.setup`, `.save_restore` into the runner.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `tst_test.h`, `config.h`, `lapi/sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TST_EXP_FAIL`, `TST_SR_TCONF`, `TST_TEST_TCONF`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare04.c

Purpose: This test case is to verify unshare(CLONE_NEWNS) also unshares process working directory.

Important APIs/types/functions: includes `tst_test.h`, `lapi/sched.h`; exercises `unshare`; defines `setup`, `cleanup`, `run`; uses constants `CLONE_FS`, `CLONE_NEWNS`, `SIGCHLD`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.needs_root`, `.needs_tmpdir`, `.test_all`, `.setup`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `tst_test.h`, `lapi/sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_PASS`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare05.c

Purpose: This test case verifies unshare(CLONE_NEWPID) creates a new PID namespace and that the first child process in the new namespace gets PID 1.

Important APIs/types/functions: includes `tst_test.h`, `lapi/sched.h`; exercises `unshare`; defines `setup`, `run`; uses constants `CLONE_NEWPID`, `SIGCHLD`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.setup`, `.needs_root`, `.test_all`, `.needs_kconfigs` into the runner. Named case hints include `CONFIG_PID_NS`.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `tst_test.h`, `lapi/sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TST_EXP_EQ_LI`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/Makefile

Purpose: build metadata for the `userfaultfd` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk; userfaultfd01: CFLAGS += -pthread; userfaultfd02: CFLAGS += -pthread; userfaultfd03: CFLAGS += -pthread; userfaultfd04: CFLAGS += -pthread; userfaultfd05: CFLAGS += -pthread; userfaultfd06: CFLAGS += -pthread; userfaultfd07: CFLAGS += -pthread`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd01.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread.

Important APIs/types/functions: includes `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`; exercises `userfaultfd`; defines `setup`, `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `O_NONBLOCK`, `PROT_READ`, `PROT_WRITE`, `UFFDIO_API`, `UFFDIO_COPY`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_MISSING`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`, `UFFD_USER_MODE_ONLY`.

Control flow centers on `setup`, `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd02.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread using UFFDIO_MOVE.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`; exercises `userfaultfd`; defines `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `PROT_READ`, `PROT_WRITE`, `UFFDIO_API`, `UFFDIO_MOVE`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_MISSING`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`, `_SC_PAGE_SIZE`.

Control flow centers on `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.test_all`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `config.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd03.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread using /dev/userfaultfd instead of syscall, using USERFAULTFD_IOC_NEW ioctl to create the uffd & UFFDIO_COPY.

Important APIs/types/functions: includes `config.h`, `poll.h`, `unistd.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`; exercises `syscall`, `userfaultfd`, `ioctl`; defines `setup`, `open_userfaultfd`, `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `O_NONBLOCK`, `O_RDWR`, `PROT_READ`, `PROT_WRITE`, `UFFDIO_API`, `UFFDIO_COPY`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_MISSING`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`.

Control flow centers on `setup`, `open_userfaultfd`, `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.needs_root`, `.setup`, `.test_all`, `.needs_kconfigs`, `.cleanup` into the runner. Named case hints include `CONFIG_USERFAULTFD=y`.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `config.h`, `poll.h`, `unistd.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd04.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread using UFFDIO_ZEROPAGE.

Important APIs/types/functions: includes `config.h`, `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`; exercises `userfaultfd`; defines `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `O_NONBLOCK`, `PROT_READ`, `PROT_WRITE`, `UFFDIO_API`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_MISSING`, `UFFDIO_ZEROPAGE`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`, `_SC_PAGE_SIZE`.

Control flow centers on `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.test_all`, `.cleanup`, `.needs_kconfigs` into the runner. Named case hints include `CONFIG_USERFAULTFD=y`.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `config.h`, `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd05.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread testing UFFDIO_WRITEPROTECT_MODE_WP. While the WP fault is pending, the write must NOT be visible. Resolve the fault by clearing WP so the writer can resume.

Important APIs/types/functions: includes `config.h`, `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`; exercises `userfaultfd`, `write`; defines `setup`, `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `O_NONBLOCK`, `PROT_READ`, `PROT_WRITE`, `UFFDIO_API`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_WP`, `UFFDIO_WRITEPROTECT`, `UFFDIO_WRITEPROTECT_MODE_WP`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`.

Control flow centers on `setup`, `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.needs_kconfigs`, `.cleanup` into the runner. Named case hints include `CONFIG_HAVE_ARCH_USERFAULTFD_WP=y`.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `config.h`, `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd06.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread testing UFFDIO_POISON. Poison the page that triggered the fault Try to read from the page: should trigger fault, get poisoned, then SIGBUS

Important APIs/types/functions: includes `config.h`, `poll.h`, `setjmp.h`, `signal.h`, `unistd.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`; exercises `userfaultfd`, `read`; defines `sigbus_handler`, `setup`, `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `O_NONBLOCK`, `PROT_READ`, `PROT_WRITE`, `SIGBUS`, `UFFDIO_API`, `UFFDIO_POISON`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_MISSING`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`.

Control flow centers on `sigbus_handler`, `setup`, `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `config.h`, `poll.h`, `setjmp.h`, `signal.h`, `unistd.h`, `tst_test.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd07.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread testing UFFDIO_CONTINUE. Populate page cache so that after MADV_DONTNEED the next access can generate a MINOR fault rather than a MISSING fault. Update the shmem page in page cache before resuming the fault.

Important APIs/types/functions: includes `config.h`, `poll.h`, `unistd.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_prw.h`, `tst_safe_pthread.h`, `lapi/memfd.h`; exercises `userfaultfd`, `memfd_create`, `madvise`; defines `setup`, `set_pages`, `reset_pages`, `run`; uses constants `MAP_SHARED`, `O_CLOEXEC`, `O_NONBLOCK`, `PROT_READ`, `UFFDIO_API`, `UFFDIO_CONTINUE`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_MINOR`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`, `UFFD_FEATURE_MINOR_SHMEM`, `UFFD_PAGEFAULT_FLAG_MINOR`, `_SC_PAGE_SIZE`.

Control flow centers on `setup`, `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `config.h`, `poll.h`, `unistd.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_prw.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ustat/Makefile

Purpose: build metadata for the `ustat` LTP syscall test directory; it selects local test binaries and delegates compilation to the common LTP testcase make system.

Important APIs/types/functions: key directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make evaluates the top-level source directory, applies local target or flag additions, then includes the generic leaf target rules that compile each testcase executable.

State and persistence behavior: no runtime state is kept here. The persistent effect is build output: generated test binaries, helper binaries, and any compile/link flags used by sibling C tests.

Dependencies and integration points: integrates with shared LTP fragments `include/mk/testcases.mk` and `include/mk/generic_leaf_target.mk`. It is the build entry point consumed by the broader LTP syscall test build.

Risks and test signals: a missing include, wrong target filter, or omitted linker flag silently removes runtime coverage. Successful build and expected executable presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat01.c

Purpose: Check that ustat() succeeds given correct parameters. Find a valid device number

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `unistd.h`, `errno.h`, `sys/types.h`, `sys/stat.h`, `lapi/syscalls.h`, `lapi/ustat.h`; exercises `ustat`, `raw syscall path`; defines `run`, `setup`; uses constants `EINVAL`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.skip_filesystems`, `.tags` into the runner. Named case hints include `btrfs`, `known-fail`. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is filesystem statistics addressed by a device number; the interface is obsolete and filesystem-dependent.

Dependencies and integration points: Depends on obsolete `ustat` syscall availability, `struct ustat` definitions from libc or lapi, and a valid device number from `stat("/")`. Direct include dependencies include `config.h`, `tst_test.h`, `unistd.h`, `errno.h`, `sys/types.h`, `sys/stat.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TST_TEST_TCONF`, `TTERRNO`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat02.c

Purpose: Test whether ustat(2) system call returns appropriate error number for invalid dev_t parameter and for bad address paramater. Find a valid device number

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `unistd.h`, `errno.h`, `sys/stat.h`, `sys/types.h`, `lapi/syscalls.h`, `lapi/ustat.h`; exercises `ustat`, `raw syscall path`; defines `run`, `setup`; uses constants `EFAULT`, `EINVAL`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test`, `.setup`, `.tcnt`, `.skip_filesystems`, `.tags` into the runner. Named case hints include `Invalid parameter`, `Bad address`, `btrfs`, `known-fail`. Error-path expectations include `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is filesystem statistics addressed by a device number; the interface is obsolete and filesystem-dependent.

Dependencies and integration points: Depends on obsolete `ustat` syscall availability, `struct ustat` definitions from libc or lapi, and a valid device number from `stat("/")`. Direct include dependencies include `config.h`, `tst_test.h`, `unistd.h`, `errno.h`, `sys/stat.h`, `sys/types.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TST_TEST_TCONF`, `TST_TOTAL`, `TTERRNO`; checks errno values `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.h

Purpose: Legacy 16-bit UID/GID syscall compatibility helpers for old LTP tests; it defines fallback syscall wrappers and range checks for old kernel ID widths.

Important APIs/types/functions: includes `errno.h`, `grp.h`, `sys/fsuid.h`, `sys/types.h`, `unistd.h`, `compat_gid.h`, `compat_uid.h`, `lapi/syscalls.h`; defines `setresuid`, `getresuid`, `setresgid`, `getresgid`, `SETGROUPS`, `GETGROUPS`, `SETUID`, `SETGID`, `SETFSUID`, `SETFSGID`, `SETREUID`, `SETREGID`; touches `syscall`, `write`, `raw syscall path`; uses constants/macros such as `TBROK`, `TCONF`, `TST_USE_COMPAT16_SYSCALL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is owned by tests that include these helpers. The headers/snippets normalize 16-bit UID/GID syscall compatibility at compile and runtime.

Dependencies and integration points: Depends on legacy/new LTP headers, `lapi/syscalls.h`, kernel old UID/GID typedefs, and build flags that select `TST_USE_COMPAT16_SYSCALL`. Direct includes: `errno.h`, `grp.h`, `sys/fsuid.h`, `sys/types.h`, `unistd.h`, `compat_gid.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.mk -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.mk

Purpose: Makefile snippet that builds both normal and `_16` variants of syscall tests and injects `TST_USE_COMPAT16_SYSCALL` for compatibility binaries.

Important APIs/types/functions: touches `syscall`, `write`; uses constants/macros such as `TST_USE_COMPAT16_SYSCALL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is owned by tests that include these helpers. The headers/snippets normalize 16-bit UID/GID syscall compatibility at compile and runtime.

Dependencies and integration points: Depends on legacy/new LTP headers, `lapi/syscalls.h`, kernel old UID/GID typedefs, and build flags that select `TST_USE_COMPAT16_SYSCALL`. Direct includes: none beyond consumers.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_gid.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_gid.h

Purpose: Small compatibility header that selects `GID_T` and `GID_SIZE_CHECK()` for either old 16-bit GID syscall variants or native `gid_t`.

Important APIs/types/functions: includes `asm/posix_types.h`, `tst_common.h`; defines `GID_SIZE_CHECK`; touches `write`; uses constants/macros such as `TST_USE_COMPAT16_SYSCALL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is owned by tests that include these helpers. The headers/snippets normalize 16-bit UID/GID syscall compatibility at compile and runtime.

Dependencies and integration points: Depends on legacy/new LTP headers, `lapi/syscalls.h`, kernel old UID/GID typedefs, and build flags that select `TST_USE_COMPAT16_SYSCALL`. Direct includes: `asm/posix_types.h`, `tst_common.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_gid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_tst_16.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_tst_16.h

Purpose: Newer LTP-harness 16-bit UID/GID compatibility helpers; it wraps set/get uid/gid/chown-family calls with `TST_CREATE_SYSCALL` and LTP `tst_brk()` failures.

Important APIs/types/functions: includes `errno.h`, `grp.h`, `sys/fsuid.h`, `sys/types.h`, `unistd.h`, `compat_gid.h`, `compat_uid.h`, `lapi/syscalls.h`; defines `setresuid`, `setresgid`, `SETGROUPS`, `GETGROUPS`, `SETUID`, `SETGID`, `SETFSUID`, `SETFSGID`, `SETREUID`, `SETREGID`, `SETRESUID`, `SETRESGID`; touches `syscall`, `raw syscall path`; uses constants/macros such as `TBROK`, `TCONF`, `TST_CREATE_SYSCALL`, `TST_USE_COMPAT16_SYSCALL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is owned by tests that include these helpers. The headers/snippets normalize 16-bit UID/GID syscall compatibility at compile and runtime.

Dependencies and integration points: Depends on legacy/new LTP headers, `lapi/syscalls.h`, kernel old UID/GID typedefs, and build flags that select `TST_USE_COMPAT16_SYSCALL`. Direct includes: `errno.h`, `grp.h`, `sys/fsuid.h`, `sys/types.h`, `unistd.h`, `compat_gid.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_tst_16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_uid.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_uid.h

Purpose: Small compatibility header that selects `UID_T` and `UID_SIZE_CHECK()` for either old 16-bit UID syscall variants or native `uid_t`.

Important APIs/types/functions: includes `asm/posix_types.h`, `tst_common.h`; defines `UID_SIZE_CHECK`; touches `write`; uses constants/macros such as `TST_USE_COMPAT16_SYSCALL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is owned by tests that include these helpers. The headers/snippets normalize 16-bit UID/GID syscall compatibility at compile and runtime.

Dependencies and integration points: Depends on legacy/new LTP headers, `lapi/syscalls.h`, kernel old UID/GID typedefs, and build flags that select `TST_USE_COMPAT16_SYSCALL`. Direct includes: `asm/posix_types.h`, `tst_common.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_uid.h -->
