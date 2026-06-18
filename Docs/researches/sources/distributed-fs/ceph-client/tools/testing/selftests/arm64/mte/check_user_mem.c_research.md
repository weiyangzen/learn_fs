# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_user_mem.c

## Purpose

This test verifies how kernel user-memory access helpers handle MTE-tagged userspace buffers during `read`, `write`, `readv`, and `writev`. It checks that invalid tags in user buffers are rejected in synchronous mode but may be accepted in asynchronous mode according to the arm64 MTE userspace ABI.

## Important APIs, Types, and Functions

`enum test_type` selects syscall families. `check_usermem_access_fault()` creates a temporary file, fills it, maps tagged memory, tags a subrange with a new allocation tag, and tries many offset/size combinations. `format_test_name()` renders kselftest names. The test uses `read()`, `write()`, `readv()`, `writev()`, `mte_set_tag_address_range()`, `mte_insert_new_tag()`, and `cur_mte_cxt`.

## Control Flow and Data Flow

`main()` initializes the page size and MTE state, then iterates over four syscall types, sync/async modes, private/shared mappings, whole-tail versus one-granule tag lengths, and page/granule tag offsets for 64 planned rows. Each row first proves a valid tagged read succeeds, mutates a selected part of the buffer to an invalid tag, then tests file and pointer offsets from 0 to 15 with sizes from 1 byte to one page.

## State and Persistence Behavior

The temporary file is unlinked after creation by the common helper and closed at test end. MTE mode is restored by `mte_restore_setup()`. Per-row memory and tag state is freed through `mte_free_memory()`.

## Dependencies and Integration Points

This is an integration test between arm64 MTE userspace tagging, kernel `copy_{to,from}_user()` paths used by file syscalls, vectored I/O, tmpfs-backed temporary files, and kselftest. It is especially relevant to filesystem and VFS paths because the kernel copies data through user pointers.

## Risks and Edge Cases

The expected length comparison in synchronous mode checks `syscall_len < len` rather than `syscall_len < size`, so a short transfer is treated as sufficient evidence of rejection. Async mode accepts full-size success. Offset loops intentionally exercise every byte alignment inside an MTE granule. Resource cleanup can be skipped on early file-fill write failure.

## Test Signals

Passing rows show no delivered SIGSEGV from kernel user access, synchronous syscalls returning short/error for invalid tags, and asynchronous syscalls completing the requested size. Any unexpected signal, valid-buffer mismatch, or wrong transfer length fails the row.
