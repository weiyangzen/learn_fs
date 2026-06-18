# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_pedit.h

## Purpose
Defines the TC packet-edit action ABI for modifying packet bytes at offsets, with extended header-type and command metadata.

## Important APIs, Types, and Constants
Attributes include legacy parameters, extended parameters, extended keys, and per-key extended metadata. Header types include network, Ethernet, IPv4, IPv6, TCP, and UDP. Commands include set and add. `struct tc_pedit_key` carries mask, value, offset, `at`, `offmask`, and shift. `struct tc_pedit_sel` embeds `tc_gen`, key count, flags, and a flexible `keys[]` array annotated with `__counted_by(nkeys)`.

## Control Flow, State, and Persistence
Userspace provides one or more edit keys. Runtime action computes offsets, applies masks/values or additions, and records generic counters. Action config persists until removed.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC, checksum action, and packet header parsers.

## Risks and Test Signals
Risks include out-of-bounds edits, legacy network-relative semantics, flexible-array sizing, and missing checksum updates. Test multiple keys, extended header types, set/add commands, malformed offsets, action dump, and packet capture plus checksum verification.
