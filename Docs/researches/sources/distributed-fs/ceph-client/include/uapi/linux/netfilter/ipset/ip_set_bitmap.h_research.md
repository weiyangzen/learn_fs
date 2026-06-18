# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_bitmap.h

## Purpose
Defines bitmap ipset type-specific error codes.

## Important APIs, Types, And Functions
Exports `IPSET_ERR_BITMAP_RANGE` and `IPSET_ERR_BITMAP_RANGE_SIZE`, starting from `IPSET_ERR_TYPE_SPECIFIC` in `ip_set.h`.

## Control Flow
Bitmap set create/add/test/delete operations report these errors when an element is outside the configured range or the requested range exceeds type size limits.

## State, Persistence, And Dependencies
State is bitmap set range and element bits in kernel ipset storage. Depends on `linux/netfilter/ipset/ip_set.h`.

## Integration Points
Used by ipset bitmap type implementations and userspace error decoding.

## Risks
Error values are ABI and must not collide with other type-specific ranges. Userspace must distinguish range validation from generic invalid address errors.

## Test Signals
Create bitmap sets with boundary ranges, add/delete/test endpoints, and assert expected errors for out-of-range and too-large ranges.
