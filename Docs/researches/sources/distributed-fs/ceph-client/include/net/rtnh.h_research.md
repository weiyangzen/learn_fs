# sources/distributed-fs/ceph-client/include/net/rtnh.h

## Purpose
This compact header provides helper routines for walking multipath route next-hop (`struct rtnexthop`) payloads embedded in rtnetlink route messages.

## Important APIs, Types, And Functions
`rtnh_ok()` validates that a next-hop record fits the remaining buffer and has at least the base header size. `rtnh_next()` advances by `NLA_ALIGN(rtnh_len)` and updates the caller's remaining byte count. `rtnh_attrs()` returns the first nested netlink attribute after the aligned next-hop header. `rtnh_attrlen()` returns the attribute payload length after subtracting the aligned base header.

## Control Flow
Route parsing loops call `rtnh_ok()` before dereferencing, process the current nexthop and attributes, then move with `rtnh_next()`. The helpers intentionally leave policy parsing to route code while centralizing length arithmetic.

## State And Persistence
The file has no persistent state. It only interprets caller-owned netlink message memory.

## Dependencies And Integration Points
It depends on `linux/rtnetlink.h` for `struct rtnexthop` and `net/netlink.h` for alignment. It is integrated by IPv4/IPv6 route netlink parsing and dump code handling `RTA_MULTIPATH`.

## Risks And Test Signals
Main risks are malformed length fields, alignment mistakes, and callers using `rtnh_attrs()` without first validating. Test signals are fuzzed rtnetlink route messages, multipath route add/delete tests, and sanitizer coverage for truncated attributes.
