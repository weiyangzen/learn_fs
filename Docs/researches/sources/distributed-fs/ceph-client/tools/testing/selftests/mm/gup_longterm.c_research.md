# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/gup_longterm.c

## Purpose
`gup_longterm.c` tests long-term `get_user_pages()`/`pin_user_pages()` behavior for file-backed mappings. It verifies which filesystems and mapping modes allow long-term read-only or writable pins, including fast-GUP variants and optionally `io_uring` fixed-buffer registration.

## Important APIs, types, and functions
The core type is `enum test_type`, covering read-only, read-only fast, read/write, read/write fast, and `io_uring` when `LOCAL_CONFIG_HAVE_LIBURING` is enabled. `get_fs_type()`, `fs_is_unknown()`, and `fs_supports_writable_longterm_pinning()` classify backing filesystems using `statfs` magic values. `do_test()` performs setup, mapping, fault-in, optional `mprotect(PROT_READ)`, and the relevant `PIN_LONGTERM_TEST_START`/`STOP` ioctl or `io_uring_register_buffers()` path. `run_with_memfd()`, `run_with_tmpfile()`, `run_with_local_tmpfile()`, and `run_with_memfd_hugetlb()` provide backing variants. `test_case` entries bind human descriptions to wrapper functions.

## Control flow
`main()` records base page size, detects supported hugetlb page sizes, opens `/sys/kernel/debug/gup_test`, sets a kselftest plan equal to test cases times backing variants, then iterates all test cases. Each run creates a file, truncates and fallocates it to the requested size, maps it shared or private, faults the pages in, and asks the kernel debugfs GUP test driver to pin the range. Return handling distinguishes unsupported ioctls, expected `EFAULT` on unsupported writable shared long-term pins, and failures where a pin should have worked.

## State and persistence behavior
The test creates transient memfds, tmpfiles, local unlinked files, and hugetlb memfds. It mutates file length, allocates blocks, faults mappings, and temporarily holds long-term pins until `PIN_LONGTERM_TEST_STOP`. It does not persist data beyond the lifetime of each file descriptor.

## Dependencies and integration points
This file integrates with the in-kernel `CONFIG_GUP_TEST` debugfs device at `/sys/kernel/debug/gup_test`, `mm/gup_test.h` UAPI structures, hugetlb page-size detection in `vm_util.h`, filesystem magic constants, and optional liburing. It relies on kernel rules that allow writable long-term shared pins only on special filesystems such as tmpfs and hugetlbfs.

## Risks and edge cases
Unknown filesystems are skipped for writable shared cases because expected behavior cannot be asserted safely. `fallocate()` failures can represent unsupported filesystems or insufficient huge pages. Running without debugfs, root, `CONFIG_GUP_TEST`, or enough hugetlb pages produces skips. The io_uring branch intentionally treats several errors as unsupported-resource skips.

## Test signals
Pass conditions are correct accept/reject behavior for each mapping/filesystem/type matrix, successful ioctl start/stop for supported cases, and expected failure for unsupported writable shared long-term pins.
