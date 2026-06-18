# sources/distributed-fs/ceph-client/net/ethtool/privflags.c

## Purpose
This file implements netlink `PRIVFLAGS_GET` and `PRIVFLAGS_SET`, exposing driver-defined private flags as named bitsets.

## Important APIs, Types, And Functions
`struct privflags_reply_data` stores allocated flag names, count, and current 32-bit flags. Core helpers are `ethnl_get_priv_flags_info()`, `privflags_prepare_data()`, `privflags_reply_size()`, `privflags_fill_reply()`, `privflags_cleanup_data()`, `ethnl_set_privflags_validate()`, and `ethnl_set_privflags()`. `ethnl_privflags_request_ops` registers GET and SET.

## Control Flow
GET validates driver support for private flags, string counts, and strings; under ethtool ops it obtains the count and names, caps usable flags to 32 after allocating enough names for all reported flags, reads current flags, and emits a named bitset. SET requires the flags attribute, detects compact versus named bitset encoding, obtains names only when needed, reads current flags, applies bitset updates, and calls `set_priv_flags()` when changed.

## State And Persistence
The file has transient allocated name arrays per request. Persistent state is the driver-maintained private flag word changed by `set_priv_flags()`.

## Dependencies And Integration Points
It depends on driver `ethtool_ops::{get_priv_flags,set_priv_flags,get_sset_count,get_strings}` and `bitset.h` helpers for `ethnl_bitset32_*`. Successful SET emits `ETHTOOL_MSG_PRIVFLAGS_NTF`.

## Risks And Edge Cases
Netlink can name more than 32 flags, but the legacy driver `get_priv_flags()` API returns only `u32`; the code warns and caps count to 32 after fetching all names. Compact bitset SET does not need names, but named SET does, so allocation failures are possible only for named mode. Drivers reporting inconsistent counts or names can make bitset updates ambiguous.

## Test Signals
Tests should cover compact and named GET/SET, more-than-32 flag reporting, missing callbacks, no-op updates, invalid bit names, allocation failure, and notification after a changed flag word.
