# sources/distributed-fs/ceph-client/fs/ceph/ceph_frag.c

## Purpose

`ceph_frag.c` implements comparison for Ceph fragment identifiers. Ceph directory fragmentation uses encoded frag values and bit widths; this helper provides a deterministic ordering for two `__u32` frag values.

## Important APIs and Functions

The only function is `ceph_frag_compare(__u32 a, __u32 b)`. It extracts the fragment value with `ceph_frag_value`, compares those values first, and if equal compares the fragment bit width from `ceph_frag_bits`. It returns `-1`, `1`, or `0` in the usual comparator style.

## Control Flow

The function is linear and branch-only: compare values, return if different; compare bit widths, return if different; otherwise return equality. There is no allocation, locking, or external state mutation.

## State and Persistence Behavior

No state is stored or persisted. The function derives ordering entirely from encoded frag arguments.

## Dependencies and Integration Points

It includes `<linux/ceph/types.h>` for the frag encoding helpers and `<linux/module.h>` for kernel compilation context. Callers elsewhere in the Ceph client can use this comparator to maintain sorted fragment structures or compare directory-fragment identifiers consistently with Ceph encoding rules.

## Risks and Edge Cases

Correctness depends on `ceph_frag_value` and `ceph_frag_bits` matching the wire/in-memory encoding. Sorting by value before bit width must match all callers’ expectations; reversing that order would change fragment tree traversal behavior. Equal encoded value and bits compare equal even if higher unused bits differ in a malformed input; validation is expected elsewhere.

## Test Signals

Unit-level tests should compare fragments with lower/higher values, identical values with lower/higher bit counts, and exact equality. Integration signals are stable ordering in directory-fragment maps and no inconsistent fragment comparisons during readdir or MDS frag updates.
