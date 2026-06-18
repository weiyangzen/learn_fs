<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/context.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/context.c

## Purpose
Implements hashing for SELinux security contexts. The hash supports SID table and context lookup paths that need a stable hash over either mapped structured contexts or unmapped invalid context strings.

## Important APIs, Types, and Functions
The single function is `context_compute_hash()`. It hashes invalid/unmapped contexts with `full_name_hash()` over `str` and `len`, and valid contexts with `jhash_3words(user, role, type)` followed by `mls_range_hash()`.

## Control Flow
If `c->len` is nonzero, the function treats the context as an invalid string representation and returns the string hash. Otherwise it hashes structured user, role, type, and MLS range fields. The code assumes contexts from different policies are not mixed for equality/hash comparisons.

## State and Persistence
No state is stored here. The returned hash feeds persistent policy/SID data structures elsewhere. It depends on the invariant that invalid contexts have only `len` and `str` set under a given policy.

## Dependencies and Integration Points
Depends on Linux jhash/name hash helpers, `context.h`, and `mls.h`. Used by SID table or context mapping code to bucket contexts consistently with `context_equal()`.

## Risks
Hash/equality invariants must match: invalid string contexts compare by string while valid contexts compare by fields. Mixing contexts from different policies could make the assumption unsafe. MLS hash changes alter table distribution.

## Test Signals
Hash equal valid contexts with identical MLS ranges, unequal user/role/type/range variants, invalid string contexts, valid versus invalid contexts with similar printed representation, and SID table lookup performance/collision behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/context.c -->
