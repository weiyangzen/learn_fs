# sources/distributed-fs/ceph-client/include/linux/ceph/ceph_frag.h

## Purpose

`ceph_frag.h` defines Ceph directory fragment encoding helpers. A fragment represents a subset of a 24-bit value space using a prefix length and value, packed into a 32-bit word with the high 8 bits holding the number of significant bits.

## Important APIs, Types, and Functions

Inline helpers are `ceph_frag_make`, `ceph_frag_bits`, `ceph_frag_value`, `ceph_frag_mask`, `ceph_frag_mask_shift`, `ceph_frag_contains_value`, `ceph_frag_make_child`, `ceph_frag_is_leftmost`, `ceph_frag_is_rightmost`, and `ceph_frag_next`. The external comparator `ceph_frag_compare()` sorts fragments in logical value-space order.

## Control Flow

Runtime flow is limited to arithmetic helpers. Callers create a fragment, test whether a hash belongs to it, split it into child fragments, advance to the next peer fragment, or compare fragments while traversing directory-fragment trees.

## State and Persistence Behavior

No state is stored here. Encoded fragments appear in CephFS wire structures such as `ceph_frag_tree_split` and MDS readdir/reply paths, so the bit layout is an ABI.

## Dependencies and Integration Points

It relies on `__u32` and `bool` from kernel headers included by users. It integrates with `ceph_fs.h` fragment tree records, directory hashing from `ceph_hash.h`, and MDS metadata layout.

## Risks and Edge Cases

Inputs assume `b <= 24`; larger values make shifts invalid. Numeric sorting of encoded fragments is explicitly wrong because the prefix length is stored in high bits. `ceph_frag_next()` can step past the rightmost fragment if callers do not check bounds.

## Test Signals

Tests should cover make/bits/value/mask round trips, child partition coverage without overlap, leftmost/rightmost detection, logical comparator ordering, and containment results for boundary hash values.
