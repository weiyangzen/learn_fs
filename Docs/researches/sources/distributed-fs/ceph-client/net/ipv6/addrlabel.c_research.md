# sources/distributed-fs/ceph-client/net/ipv6/addrlabel.c

## Purpose
`addrlabel.c` implements the IPv6 address label policy table used by default source address selection. Labels follow RFC 6724 with Linux extensions and are exposed through rtnetlink `RTM_NEWADDRLABEL`, `RTM_DELADDRLABEL`, and `RTM_GETADDRLABEL`. `addrconf.c` calls `ipv6_addr_label()` while scoring source addresses.

## Important APIs, Types, and Functions
- `struct ip6addrlbl_entry`: one policy row containing prefix, prefix length, optional ifindex selector, special address type selector, label value, RCU hlist node, and RCU free head.
- `ip6addrlbl_init_table[]`: per-net default policy entries for `::/0`, ULA, site-local, 6to4, 6bone, Teredo, ORCHID, IPv4-mapped, IPv4-compatible, and loopback labels.
- `ipv6_addr_label()`: exported lookup-style function returning a label for an address/type/ifindex or `IPV6_ADDR_LABEL_DEFAULT` when no row matches.
- `ip6addrlbl_alloc()`, `__ip6addrlbl_add()`, `ip6addrlbl_add()`, `__ip6addrlbl_del()`, `ip6addrlbl_del()`: allocation and mutation helpers that normalize prefixes, validate special mapped/compat/loopback prefix lengths, keep rows sorted, and update sequence numbers.
- `ip6addrlbl_net_init()` and `ip6addrlbl_net_exit()`: per-net namespace setup and teardown of the label table.
- Rtnetlink handlers: `ip6addrlbl_newdel()`, `ip6addrlbl_get()`, `ip6addrlbl_dump()`, `ipv6_addr_label_rtnl_register()`.

## Control Flow
- Initialization registers a per-net subsystem; each namespace initializes a spinlock and hlist head, then inserts the default table rows with `ip6addrlbl_add()`.
- Lookup masks the caller's address type down to mapped/compatible/loopback bits, enters RCU, scans the sorted hlist, and returns the first row matching ifindex, address type, and prefix. Longest-prefix ordering makes first match the best match.
- Add/replace parses netlink attributes, rejects non-AF_INET6 and invalid prefix length/label, checks ifindex existence, allocates a normalized row, and inserts under `ip6addrlbl_table.lock`. Replacement swaps the existing hlist node using RCU and frees the old row after grace period.
- Delete normalizes the requested prefix and removes an exact prefix length, ifindex, and prefix match under the table lock.
- Dump validates strict requests, snapshots `seq`, iterates rows under RCU from `cb->args[0]`, and emits `ifaddrlblmsg` with address and label attributes. Get requires a /128 query address and returns the matching row for that full address.

## State and Persistence Behavior
- State is per network namespace in `net->ipv6.ip6addrlbl_table`, including an RCU hlist, spinlock, and sequence counter.
- Rows are dynamic kernel allocations and are not persisted outside the running namespace. Defaults are recreated on namespace initialization.
- Readers are lockless under RCU; writers serialize with a spinlock and use `hlist_*_rcu()` plus `kfree_rcu()`. The sequence is incremented on successful add/replace to support dump consistency.

## Dependencies and Integration Points
- Uses core address helpers from `addrconf_core.c`, especially `ipv6_addr_type()`, `ipv6_prefix_equal()`, and well-known address constants.
- Feeds `addrconf.c` source selection rule "Prefer matching label" through `ipv6_addr_label()`.
- Exposes policy management to userspace through rtnetlink and is commonly exercised by `ip addrlabel`.

## Risks and Edge Cases
- Ordering in `__ip6addrlbl_add()` is security/behavior-sensitive: the table must prefer longer prefixes and ifindex-specific entries correctly. Bad ordering changes source-address selection globally.
- Special address types have strict prefix-length rules; mapped addresses longer than /96 are rejected, while broader mapped prefixes lose the special type constraint.
- Netlink handlers reject the sentinel label `0xffffffff`, because that value represents "no policy."
- Get requires prefix length 128 and an address attribute; dump strictness rejects nonzero header fields and trailing attributes.
- If default table initialization fails partway through, the error path removes rows already inserted; changes must preserve that cleanup.

## Test Signals
- `ip addrlabel list`, `ip addrlabel add`, `replace`, and `del` for global, ifindex-scoped, ULA, mapped, compat, and loopback prefixes.
- Source address selection tests where destination and candidate source labels match or mismatch.
- Network namespace creation/destruction should produce independent default tables and clean RCU-free teardown.
- Strict rtnetlink tests for unsupported attributes, invalid family, invalid prefix length, missing address/label, sentinel label, nonexistent ifindex, and `/128` get behavior.
