# sources/distributed-fs/ceph-client/init/initramfs_test.c

## Purpose
This KUnit suite validates the initramfs `newc` cpio extractor. It builds in-memory cpio streams, calls `unpack_to_rootfs()`, and verifies resulting filesystem objects or expected parse failures.

## Important APIs, Types, And Functions
- `struct initramfs_test_cpio` models the 13 `newc` header fields plus filename and data pointers.
- `fill_cpio()` serializes one or more test records into a properly padded cpio stream.
- Test cases include `initramfs_test_extract`, `initramfs_test_fname_overrun`, `initramfs_test_data`, `initramfs_test_csum`, `initramfs_test_hardlink`, `initramfs_test_many`, `initramfs_test_fname_pad`, and `initramfs_test_fname_path_max`.
- `kunit_test_init_section_suites()` registers the suite for init-section execution while keeping case metadata in `__refdata`.

## Control Flow
Each case allocates a source buffer, fills records, calls `unpack_to_rootfs()`, then checks results with init-time VFS helpers such as `init_stat`, `filp_open`, `kernel_read`, `init_unlink`, and `init_rmdir`. Cleanup removes created test files/directories.

## State And Persistence
Tests intentionally mutate rootfs by creating files, directories, and hardlinks, then remove them. Some negative tests verify that malformed records do not create visible files. The checksum failure test documents that a bad checksum can leave the file whose payload was already written while aborting later entries.

## Dependencies And Integration Points
The suite depends on KUnit, `initramfs_internal.h`, init syscall wrappers, VFS file operations, and timekeeping. It is part of early init test execution, not normal userspace-driven testing.

## Risks And Edge Cases
The suite covers historical bug-prone areas: filenames lacking NUL terminators, archive padding that permits data alignment, `PATH_MAX` acceptance/skipping, missing trailer cleanup for hardlink hash state, and checksum validation. It relies on writable rootfs state and must carefully unlink artifacts to avoid contaminating later tests.

## Test Signals
Passing this suite indicates the extractor handles normal file/dir extraction, metadata ownership/mode/mtime expectations, file contents, checksums, hardlinks, scalability across many records, padded filename fields, and path-length rejection. Failures provide direct evidence of parser or VFS integration regressions.
