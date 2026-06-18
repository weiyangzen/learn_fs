# sources/distributed-fs/ceph-client/net/ethtool/eee.c

## Purpose
This file implements ethtool netlink GET/SET support for Energy Efficient Ethernet settings. It exposes supported, advertised, and link-partner EEE link modes plus enablement and TX LPI controls.

## Important APIs, Types, And Functions
Important local types are `eee_req_info` and `eee_reply_data`. Public objects are `ethnl_eee_get_policy`, `ethnl_eee_set_policy`, and `ethnl_eee_request_ops`. Core functions are `eee_prepare_data()`, `eee_reply_size()`, `eee_fill_reply()`, `ethnl_set_eee_validate()`, and `ethnl_set_eee()`.

## Control Flow
GET requires `get_eee`, calls it inside ops bracketing, sizes and emits advertised/supported modes as a value/mask bitset, emits peer advertised modes as a list bitset, then emits active/enabled/TX-LPI fields. SET requires both get and set callbacks, reads current EEE state, applies a link-mode bitset update to `advertised`, updates boolean and timer fields, exits if unchanged, and calls `set_eee()`.

## State, Persistence, And Dependencies
State is held by the driver and represented as `struct ethtool_keee`. The file mutates only a local copy before calling `set_eee()`. Dependencies include shared link mode names, bitset helpers, ethtool ops, and generic netlink request infrastructure.

## Integration Points
The request ops register EEE GET/SET/notification behavior in the ethtool netlink dispatcher. Link mode bit naming is shared with link modes and FEC handling through `common.c`.

## Risks
EEE settings combine advertised capabilities and policy booleans; allowing unsupported advertised bits depends on driver validation in `set_eee()`. Timer units and boolean u8 conversion must match userspace ABI. Compact and verbose bitset behavior must remain consistent for large link-mode bitmaps.

## Test Signals
Test unsupported callbacks, GET reply sizing for compact/verbose mode, advertised mode updates by name and index, enable/TX-LPI toggles, TX LPI timer updates, no-op SET, and driver rejection of invalid advertised combinations.
