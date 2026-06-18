<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/tcache.h -->
# sources/distributed-fs/orangefs/src/common/misc/tcache.h

## Purpose
Declares the generic timeout cache interface and data structures used by OrangeFS components that need keyed, expiring, in-memory objects.

## Important APIs, Types, And Functions
Defines `enum PINT_tcache_replace_algorithms`, currently `LEAST_RECENTLY_USED`; `struct PINT_tcache_entry`, containing payload, expiration, hash link, and LRU link; `struct PINT_tcache`, containing callbacks, options, hash table, and LRU list; and `enum PINT_tcache_options` for timeout, entry count, hard/soft limits, enable flags, reclaim percentage, replacement algorithm, and expiration enablement. It declares all `PINT_tcache_*` entry points implemented in `tcache.c`.

## Control Flow
The header documents the expected lifecycle: initialize with callbacks, insert payloads, lookup entries and copy payload data before later cache calls if needed, optionally refresh or delete entries, and finalize to free all owned payloads.

## State And Persistence
The structures describe only process memory. The comments define ownership rules: keys are immutable after insertion, payload memory is caller allocated but cache owned after insertion, and callers must provide synchronization.

## Dependencies And Integration Points
Includes `pvfs2-internal.h`, `sys/time.h` or `wincommon.h`, `pvfs2-types.h`, `quicklist.h`, and `quickhash.h`. It is consumed by client capability caching and any other higher-level OrangeFS cache requiring timeout/LRU semantics.

## Risks And Test Signals
Risks are contract drift between comments and implementation, enum option values reused directly by wrappers, and portability differences around `struct timeval`. Compile tests should include Unix and Windows paths; behavioral tests should validate the ownership and non-thread-safe assumptions through wrapper-level locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/tcache.h -->
