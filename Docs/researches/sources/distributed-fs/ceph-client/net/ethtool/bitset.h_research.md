# sources/distributed-fs/ceph-client/net/ethtool/bitset.h

## Purpose
This header declares the ethtool netlink bitset helper API shared by feature-specific handlers. It standardizes the string-array type used for named bits and caps accepted bitset size.

## Important APIs, Types, And Functions
`ETHNL_MAX_BITSET_SIZE` limits parsed bitset sizes to `S16_MAX`. `ethnl_string_array_t` represents an array of fixed-width ethtool string names. Declared helpers cover compact detection, reply-size calculation, netlink emission, update-in-place for `unsigned long` and `u32` bitmaps, and parsing to value/mask bitmaps.

## Control Flow
The header has no executable flow. Callers include it, pass their current bitmap plus optional mask/name arrays, and rely on `bitset.c` to calculate reply sizes, serialize replies, parse user input, and report whether state changed.

## State, Persistence, And Dependencies
The header owns no state. It depends on Linux ethtool and netlink types, `struct sk_buff`, `struct nlattr`, and `struct netlink_ext_ack`.

## Integration Points
`debug.c`, `eee.c`, `features.c`, `fec.c`, and other ethtool netlink handlers include this header to expose named capability sets through a common ABI. The API preserves a consistent compact/verbose representation across the whole ethtool generic netlink family.

## Risks
Changing prototypes or the max-size constant can break many handlers and userspace ABI assumptions. The `ethnl_string_array_t` fixed-width string convention matters because many kernel ethtool string tables are not ordinary null-terminated dynamic strings.

## Test Signals
Build coverage across all ethtool netlink handlers is the first signal. ABI tests should confirm all users of bitsets still accept compact and verbose forms and still reject malformed oversize payloads.
