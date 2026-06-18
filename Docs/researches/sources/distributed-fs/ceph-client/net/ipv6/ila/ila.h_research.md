# sources/distributed-fs/ceph-client/net/ipv6/ila/ila.h

## Purpose
Defines shared ILA data structures and function declarations for locator/identifier address translation, lwtunnel support, per-network xlat state, and generic-netlink commands.

## Important APIs, Types, and Functions
Types include `struct ila_locator`, `struct ila_identifier`, `struct ila_addr`, `struct ila_params`, and `struct ila_net`. Inline helpers include `ila_a2i()`, `compute_csum_diff8()`, and `ila_csum_neutral_set()`. It declares `ila_update_ipv6_locator()`, `ila_init_saved_csum()`, lwt lifecycle functions, xlat pernet functions, xlat netlink command handlers, `ila_net_id`, and `ila_nl_family`.

## Control Flow
The header has no execution path but encodes the ILA address layout: IPv6 address high 64 bits are locator, low 64 bits are identifier, with bitfields for identifier type and checksum-neutral flag. `compute_csum_diff8()` constructs a checksum delta over two 64-bit locator values for later incremental checksum updates.

## State and Persistence
Defines per-translation parameters (`locator`, `locator_match`, precomputed checksum diff, checksum mode, identifier type) and per-net xlat hashtable/lock state. Actual allocation and lifecycle are in implementation files.

## Dependencies and Integration Points
Depends on kernel byte-order bitfield definitions, checksum APIs, genetlink, skbuff, IPv6 protocol headers, and UAPI `linux/ila.h`. It is shared by lwtunnel, xlat, common checksum, and module registration code.

## Risks and Test Signals
Risks include bitfield layout portability, aliasing `struct in6_addr` to `struct ila_addr`, checksum delta correctness, and keeping declarations synchronized with `ila_xlat.c`. Test signals include sparse/endian builds, formatted identifier parsing, checksum-neutral bit behavior, and genl/lwt users compiling against this header.
