# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_hash.h

## Purpose
Defines hash ipset type-specific error codes.

## Important APIs, Types, And Functions
Exports `IPSET_ERR_HASH_FULL`, `IPSET_ERR_HASH_ELEM`, `IPSET_ERR_INVALID_PROTO`, `IPSET_ERR_MISSING_PROTO`, `IPSET_ERR_HASH_RANGE_UNSUPPORTED`, and `IPSET_ERR_HASH_RANGE`.

## Control Flow
Hash set operations return these errors when tables are full, elements are null/invalid, protocol constraints fail, or ranges are unsupported/invalid.

## State, Persistence, And Dependencies
State persists in hash set buckets and elements. Depends on `ip_set.h`.

## Integration Points
Used by hash-based ipset types and userspace diagnostics.

## Risks
Range support is type/revision-specific. Protocol fields may be mandatory for some set dimensions and invalid for others.

## Test Signals
Exercise full-table behavior, null elements, protocol-required and invalid-protocol cases, unsupported range adds, and hash resize behavior.
