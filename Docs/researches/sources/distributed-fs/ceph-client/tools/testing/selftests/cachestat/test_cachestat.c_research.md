# sources/distributed-fs/ceph-client/tools/testing/selftests/cachestat/test_cachestat.c

## Purpose

This kselftest validates the `cachestat` syscall on invalid fds, device/proc files, normal files, fsync behavior, shmem files, and mmap-populated files. It checks that cached plus evicted page counts match expected ranges and that fsync clears dirty pages on non-tmpfs files.

## Important APIs, Types, and Functions

Key functions are `print_cachestat`, `write_exactly`, `is_on_tmpfs`, `test_cachestat`, `file_type_str`, `run_cachestat_test`, and `main`. It uses `struct cachestat`, `struct cachestat_range`, `syscall(__NR_cachestat, ...)`, `open`, `shm_open`, `ftruncate`, `mmap`, `fsync`, `fstatfs`, `TMPFS_MAGIC`, `/dev/urandom`, and kselftest reporting. `NR_TESTS` is `9`; `dev_files` covers `/dev/zero`, `/dev/null`, `/dev/urandom`, `/proc/version`, and `/proc`.

## Control Flow

`main` first probes syscall availability with a bad fd and expects `EBADF` or skips on `ENOSYS`. It then iterates device/proc files, tests a created normal file with random data, repeats normal-file testing with fsync validation, and runs shmem and mmap tests over a half-file page range. Helpers write exact random buffers, call cachestat, print counters, and validate `nr_cache + nr_evicted` against expected page counts.

## State and Persistence Behavior

Temporary files `tmpfilecachestat` and `tmpshmcstat` are created and removed/unlinked. mmap memory and file descriptors are process-local. The test may leave temporary files only on early fatal paths.

## Dependencies and Integration Points

It depends on the cachestat syscall, page cache behavior, tmpfs/shmem, `/dev/urandom`, kernel headers, and kselftest. It integrates directly with VM/file-cache syscall regression coverage.

## Risks and Test Signals

Risks include page-cache races, filesystem-specific fsync semantics, tmpfs skip behavior, missing `munmap` in the mmap helper, and huge-page/readahead effects changing counters. Signals are `EBADF` recognition, zero syscall return for supported files, expected cached/evicted totals, skipped fsync on tmpfs, and dirty count zero after fsync.
