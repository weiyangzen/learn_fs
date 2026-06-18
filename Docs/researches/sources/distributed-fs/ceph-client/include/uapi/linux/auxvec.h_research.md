<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auxvec.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/auxvec.h

## Purpose
Defines generic Linux ELF auxiliary vector entry ids placed on a new program's initial stack.

## Important APIs, Types, And Functions
Exports `AT_*` constants for program headers, page size, interpreter base, entry point, uid/gid/euid/egid, platform strings, hardware capability words, clock tick, secure mode, random bytes, rseq feature size/alignment, executable filename, and minimum signal stack size. It includes architecture-specific auxvec additions first.

## Control Flow
During exec, the kernel builds an auxiliary vector of type/value pairs. The dynamic loader and libc read entries to locate ELF headers, determine platform/hwcap optimizations, seed randomness, enable secure mode behavior, and configure rseq/signal-stack expectations.

## State And Persistence
Auxv data is per exec image and remains readable through process startup mechanisms such as `getauxval()` or `/proc/self/auxv`. It is not persistent beyond the process.

## Dependencies And Integration Points
Depends on `<asm/auxvec.h>` for architecture-specific entries. Integrates with ELF loaders, libc, CPU feature dispatch, security mode handling, rseq, and procfs auxv exposure.

## Risks And Edge Cases
Architecture-specific entries can overlap if not coordinated, secure-mode handling is security-sensitive, `AT_RANDOM` points to process memory, and hardware capability interpretation is arch-specific.

## Test Signals
Exec/getauxval tests, `/proc/self/auxv` parsing, dynamic-loader startup tests, secure-exec behavior, hwcap dispatch checks, and rseq auxv value validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auxvec.h -->
