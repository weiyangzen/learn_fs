<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quickhash/quickhash.h -->
# sources/distributed-fs/orangefs/src/common/quickhash/quickhash.h

## Purpose
Implements a small chained hash table as static inline functions and macros, usable in user-space OrangeFS code and Linux kernel contexts.

## Important APIs, Types, And Functions
Defines `struct qhash_table`, `qhash_init`, `qhash_finalize`, `qhash_add`, `qhash_search`, indexed search/remove helpers, `qhash_destroy_and_finalize`, and hash helpers `quickhash_32bit_hash`, `quickhash_64bit_hash`, and `quickhash_string_hash`. It maps allocation, list, and locking primitives to kernel APIs under `__KERNEL__` and to `quicklist`/malloc/free in user space.

## Control Flow
Initialization allocates a table header and an array of list heads. Add hashes the key and appends to the target bucket. Search locks the table, scans the bucket with the caller-provided compare function, unlocks, and returns the embedded link. Removal variants unlink the matching item before returning it. The destroy macro drains every bucket and invokes a caller-supplied destructor.

## State And Persistence
Hash state is in memory: bucket array, table size, callbacks, and a kernel spinlock when compiled in kernel mode. User-space lock macros are no-ops, so concurrency must be provided externally.

## Dependencies And Integration Points
Used by `tcache`, `security-hash`, and statecomp code generation. It depends on `quicklist.h`, `pvfs2-internal.h`, and kernel list/spinlock APIs in kernel builds.

## Risks And Test Signals
The integer and string hash helpers mask with `table_size - 1`, which distributes correctly for power-of-two sizes but conflicts with comments and users that pass primes such as 1009. Search returns pointers after unlocking, making concurrent mutation unsafe. Tests should cover add/search/remove, duplicate replacement users, all destroy paths, kernel/user compilation, and hash distribution for the table sizes actually used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quickhash/quickhash.h -->
