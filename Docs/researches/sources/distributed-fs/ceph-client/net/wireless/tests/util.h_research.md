# sources/distributed-fs/ceph-client/net/wireless/tests/util.h

## Purpose
`util.h` declares shared fixtures and helpers for cfg80211 KUnit tests.

## Important APIs, Types, And Functions
It defines the `CHAN2G()` initializer macro, static `channels_2ghz` table for channels 1 through 14, `struct t_wiphy_priv`, `T_WIPHY(test, ctx)`, `t_wiphy_ctx(wiphy)`, prototypes for `t_wiphy_init()`/`t_wiphy_exit()`, and `t_skb_remove_member()` for packed SKB structure manipulation.

## Control Flow
The `T_WIPHY()` macro allocates a KUnit resource backed by `t_wiphy_init()` and asserts success. `t_skb_remove_member()` performs an in-place `memmove()` and `skb_trim()` to remove a structure member from the tail-packed SKB data used in tests.

## State And Persistence
The header provides static channel fixture data and defines the private state layout used by `util.c`: test pointer, ops pointer, caller context, supported-band object, and mutable channel array.

## Dependencies And Integration Points
It depends on cfg80211 and KUnit types being available to including tests. `tests/scan.c` uses `T_WIPHY()`, `t_wiphy_ctx()`, channel fixtures, and `t_skb_remove_member()` when building synthetic MLO frames.

## Risks And Edge Cases
`channels_2ghz` is a header-local static array, so each translation unit gets its own copy. The SKB member-removal macro assumes the member being removed is in the final packed structure currently at the end of the SKB; misuse can corrupt test frames. Fixture channel data has no rates or advanced band capabilities unless tests add them.

## Test Signals
Compile coverage from all cfg80211 KUnit tests validates macro/type consistency. Runtime use by scan tests validates channel lookup and context recovery through `t_wiphy_ctx()`.
