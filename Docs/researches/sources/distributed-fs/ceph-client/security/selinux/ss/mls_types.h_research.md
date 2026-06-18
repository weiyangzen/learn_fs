<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls_types.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/mls_types.h

## Purpose
Defines the basic MLS data structures and dominance predicates used throughout SELinux. It represents a level as sensitivity plus category set, and a range as low/high levels.

## Important APIs, Types, and Functions
Types are `struct mls_level` and `struct mls_range`. Inline predicates are `mls_level_eq()`, `mls_level_dom()`, `mls_level_incomp()`, `mls_level_between()`, and `mls_range_contains()`.

## Control Flow
MLS validation and transition code compare levels by sensitivity ordering plus category containment. Range containment checks that the candidate low dominates the allowed low and the allowed high dominates the candidate high. Between checks combine two dominance tests.

## State and Persistence
The structures are embedded in contexts, user definitions, levels, and range transition data. Category ebitmaps require explicit lifecycle management by the surrounding context or policy object.

## Dependencies and Integration Points
Depends on `security.h` and `ebitmap.h`. Used by `context.h`, `mls.c`, constraint evaluation, user range setup, and label transition logic.

## Risks
Sensitivity values are policy indexes, while categories are zero-based ebitmap positions in many call paths. Dominance semantics are security-critical and must stay consistent with MLS policy language expectations. Macros evaluate arguments more than once only through nested calls, so callers should avoid side-effect expressions.

## Test Signals
Test equality, dominance, incomparability, between, and range containment for empty and populated categories, boundary sensitivities, and category sets that differ only by one bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls_types.h -->
