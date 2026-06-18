# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/memory-failure.c

## Purpose

`memory-failure.c` is a kselftest harness suite for memory poisoning behavior. It injects hard and soft memory failures into anonymous, clean page-cache, and dirty page-cache pages and validates signals, page replacement, hardware-corrupted accounting, and kpageflags state.

## Important APIs, Types, and Functions

`enum inject_type` selects `MADV_HWPOISON` or `MADV_SOFT_OFFLINE`; `enum result_type` captures expected outcomes by mapping type. The fixture stores page size, original PFN, original `HardwareCorrupted` size, pagemap and kpageflags fds, and a trigger flag. Helpers include `madv_hard_inject()`, `madv_soft_inject()`, `sigbus_action()`, `prepare()`, `check_memory()`, `check()`, `cleanup()`, `prepare_file()`, and `get_fs_type()`.

## Control Flow

Fixture setup installs a SIGBUS handler and opens `/proc/self/pagemap` and `/proc/kpageflags`. Each test maps and initializes one page, records its PFN and current corruption accounting, injects poison once, then forces a read. Hard poisoned anonymous and dirty page-cache pages are expected to raise `SIGBUS` and leave a swapped/hwpoison entry. Soft-offlined anonymous and page-cache cases, plus hard clean page-cache, are expected not to signal and to preserve contents while changing PFN. Cleanup unpoisons the original PFN and checks the hardware-poison flag and accounting are restored.

## State and Persistence Behavior

The test directly changes kernel hardware-poison state for a PFN and relies on `unpoison_memory()` to clear it. It creates and unlinks temporary page-cache test files. It also reads global `/proc` accounting, so concurrent memory-failure activity can affect assertions.

## Dependencies and Integration Points

It depends on `vm_util.h` helpers for PFN, flags, corruption size, and unpoisoning, plus permission to read pagemap/kpageflags and use poison madvise operations. Page-cache tests skip unsupported filesystems such as tmpfs.

## Risks and Edge Cases

This is high-privilege and kernel-stateful. Failure before cleanup can leave a poisoned page until external recovery. The test excludes tmpfs page-cache cases because semantics differ. It assumes exact `HardwareCorrupted` growth by `page_size / 1024`, so system-wide noise can break it.

## Test Signals

Success requires correct SIGBUS metadata for hard failures, unchanged data and PFN replacement for recoverable cases, `KPF_HWPOISON` set after injection, and cleared poison plus restored accounting after cleanup.
