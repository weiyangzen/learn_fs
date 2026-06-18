# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag310.c

## Purpose
Implements `/dev/diag` ioctl support for DIAG 0x310 memory topology information. It queries supported subcodes, stride length, topology map sizes by nesting level, and copies topology maps to userspace.

## Important APIs, Types, And Functions
Externally used ioctl handlers are `diag310_memtop_stride()`, `diag310_memtop_len()`, and `diag310_memtop_buf()`. Internal helpers include `diag310()`, `diag310_get_subcode_mask()`, `diag310_get_memtop_stride()`, `diag310_get_memtop_size()`, `diag310_store_topology_map()`, `diag310_check_features()`, `memtop_get_stride_len()`, and `memtop_get_page_count()`.

## Control Flow
Each ioctl checks SCLP/DIAG 310 feature availability and required subcodes. Stride and page counts are lazily cached. `diag310_memtop_len()` receives a nesting level through the same userspace word it later overwrites with byte length. `diag310_memtop_buf()` reads level and target userspace address, allocates page-aligned vmalloc memory, requests subcode 5 to fill the topology map, then copies the buffer to userspace.

## State And Persistence
Static caches store feature availability, stride, and page counts per level. They persist until reboot. No filesystem persistence is used.

## Dependencies And Integration Points
Depends on SCLP capability bits, DIAG 310 return-code format, vmalloc, UAPI `struct diag310_memtop`, and `/dev/diag` dispatch in `diag_misc.c`.

## Risks And Edge Cases
Level bounds are 1 through 6. Cached sizes may become stale if firmware topology characteristics change after boot. Large page-count responses can create large allocations. User address is carried as a `u64`, requiring careful compat behavior.

## Test Signals
Signals include `/dev/diag` ioctl tests for stride, length, and buffer reads, unsupported subcode paths, invalid level handling, `-ENODATA` and `-EOVERFLOW` paths, and topology-map format validation.
