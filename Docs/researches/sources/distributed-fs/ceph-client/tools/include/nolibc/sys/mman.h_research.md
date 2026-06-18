# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/mman.h

## Purpose
Provides memory mapping wrappers for nolibc.

## APIs, Types, and Functions
Defines `_sys_mmap`/`mmap`, `_sys_mremap`/`mremap`, and `_sys_munmap`/`munmap`, including architecture-specific mmap argument handling when an arch backend overrides `_sys_mmap`.

## Control Flow, State, and Persistence
Wrappers issue mapping syscalls, return `MAP_FAILED` with errno on failure, and otherwise return mapped addresses or zero success. Persistent state is kernel VMA state owned by the process, not the header.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h`, and `<linux/mman.h>`. It is used by nolibc `malloc`, tests, and any program needing raw mappings.

## Risks and Test Signals
Risks include page-size alignment, offset width on 32-bit, architecture-specific mmap ABI differences, and leaking mappings on error paths. Test signals are anonymous/file-backed mappings, mremap growth/move behavior, munmap boundaries, and 32-bit offset tests.
