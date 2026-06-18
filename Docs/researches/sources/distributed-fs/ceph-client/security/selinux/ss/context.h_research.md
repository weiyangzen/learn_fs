<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/context.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/context.h

## Purpose
Defines the internal SELinux security context representation and inline helpers for copying, comparing, destroying, and manipulating MLS ranges. A context combines user, role, type, optional invalid string representation, and MLS low/high levels.

## Important APIs, Types, and Functions
The central type is `struct context`. Helpers include `mls_context_init()`, `mls_context_cpy()`, `mls_context_cpy_low()`, `mls_context_cpy_high()`, `mls_context_glblub()`, `mls_context_equal()`, `mls_context_destroy()`, `context_init()`, `context_cpy()`, `context_destroy()`, `context_equal()`, and `context_compute_hash()`.

## Control Flow
Copy helpers duplicate MLS category bitmaps and roll back already-copied levels on failure. Low/high helpers collapse ranges to a single level. `mls_context_glblub()` computes the intersection of two ranges by choosing greatest low sensitivity, least high sensitivity, and category intersections. `context_equal()` compares invalid contexts by string when both have `len`, rejects one-valid/one-invalid pairs, and otherwise compares structured fields.

## State and Persistence
Context state is embedded in policydb, SID table, inode/socket/task security structures, and transition computations. The optional `str` stores contexts that cannot be mapped under the current policy. MLS category bitmaps require explicit destruction.

## Dependencies and Integration Points
Depends on `ebitmap`, `mls_types`, and `security.h`. Used by services, SID table, MLS operations, policy conversion, and label computation paths.

## Risks
Memory ownership is subtle: failed MLS copy must free partial category bitmaps and duplicated strings. `context_cpy()` uses `GFP_ATOMIC`, constraining allocation contexts. The invalid-string convention must remain consistent with hashing and equality.

## Test Signals
Test valid and invalid context equality, copy/destroy with fault injection, low/high/glblub range computations, category bitmap rollback on allocation failure, and SID table operations across policy reload/conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/context.h -->
