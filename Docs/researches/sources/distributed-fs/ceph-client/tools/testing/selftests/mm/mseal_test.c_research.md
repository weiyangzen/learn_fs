# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mseal_test.c

## Purpose

`mseal_test.c` is a large functional test suite for the `mseal` syscall. It verifies that sealed VMAs resist destructive or permission-changing operations while nonsealed controls still behave normally. It covers sealing ranges across VMA boundaries, invalid inputs, `mprotect`, `munmap`, `mremap`, fixed `mmap`, `madvise`, pkeys, and merge/split behavior.

## Important APIs, Types, and Functions

The file uses direct syscall wrappers for `mseal`, `mprotect`, `pkey_mprotect`, `munmap`, `madvise`, `mremap`, and `pkey_alloc`. It has pkey register helpers for x86 PKRU (`__read_pkey_reg()`, `__write_pkey_reg()`, `set_pkey_bits()`, `set_pkey()`). Mapping helpers include `get_vma_size()`, `setup_single_address()`, `setup_single_address_rw()`, `clean_single_address()`, `seal_single_address()`, `seal_support()`, and `pkey_supported()`.

## Control Flow

`main()` probes sealing support, prints pkey availability, sets a plan of 88, and runs paired control/sealed versions for most operations. Initial tests cover adding seals, unmapped start/middle/end ranges, multiple VMAs, split-at-start/end, invalid flags, unaligned addresses, overflow, zero length, duplicate sealing, and address zero. `mprotect` tests check full, partial, unaligned-length, cross-VMA, gap, merge, and split cases. `munmap` tests cover full ranges, multiple VMAs, gaps, partial sealed tails, and already-freed start/middle/end regions. `mremap` tests cover shrink, expand, move, fixed move, fixed zero address, and `MREMAP_DONTUNMAP`. `mmap` tests cover fixed overwrite, expansion, and shrink. `madvise` tests distinguish discard-like operations on sealed read-only anonymous memory from nondiscard advice and from RW, pkey-writable, shared, or file-backed mappings. `test_seal_merge_and_split()` performs detailed VMA size checks after repeated seal splits and merges.

## State and Persistence Behavior

The suite creates many anonymous and memfd-backed mappings. Sealed mappings intentionally cannot be unmapped by normal cleanup, so failures can leave VMAs until process exit. Pkey tests allocate protection keys and modify PKRU state. The zero-address test maps address 0 with `MAP_FIXED`, seals it, and verifies protection changes fail.

## Dependencies and Integration Points

It depends on `__NR_mseal`, 64-bit kernel support, `mseal_helpers.h`, kselftest, optional x86 pkeys, `memfd_create`, and `/proc/self/maps` parsing. It integrates with core mm VMA mutation paths: permission changes, unmapping, remapping, fixed mapping replacement, advice that discards contents, VMA merge/split logic, and pkey write permission evaluation.

## Risks and Edge Cases

The test uses direct syscalls and void-pointer arithmetic under GNU C. Some test names are invoked twice, and one duplicate function signature appears in the source around `test_seal_mmap_overwrite_prot`, which should be watched in builds. Macro-based early returns can skip cleanup. The fixed zero mapping can be blocked by low-address policy on some systems. Pkey behavior is architecture- and CPU-dependent and skipped if unsupported.

## Test Signals

Success requires sealed ranges to reject `mprotect`, `munmap`, destructive `mremap`, fixed overwrite/resize `mmap`, and discard-style `madvise` where applicable, usually with `EPERM`; unsealed controls must succeed. VMA size/protection checks from `/proc/self/maps` verify split and merge outcomes. Pkey tests verify discard denial depends on effective write permission.
