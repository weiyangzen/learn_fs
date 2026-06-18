# File Research: sources/block-storage/kvdo/vdo/thread-config.h

This header defines `struct thread_config`, containing zone counts, total thread count, special-purpose thread ids, and arrays for logical, physical, hash, and bio threads.

It declares construction/freeing and thread-name formatting. Inline getters return the thread id for a logical, physical, or hash zone after log-only bounds assertions. Note the assertions use `<=` against counts, so callers must still pass valid zero-based zone indexes to avoid out-of-range array access.
