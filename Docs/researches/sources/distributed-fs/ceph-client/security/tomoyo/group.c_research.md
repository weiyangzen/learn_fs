# sources/distributed-fs/ceph-client/security/tomoyo/group.c

## Purpose

`group.c` implements TOMOYO path, number, and address group member policy. Groups let ACLs refer to reusable sets through `@group` operands instead of duplicating many path patterns, numeric ranges, or IP address ranges.

## Important APIs, types, and functions

`tomoyo_write_group()` parses and updates `path_group`, `number_group`, and `address_group` directives. `tomoyo_path_matches_group()`, `tomoyo_number_matches_group()`, and `tomoyo_address_matches_group()` are exported matchers used by file, network, and condition checks. Duplicate helpers compare path group names by interned pointer, number groups by full `tomoyo_number_union`, and address groups by `tomoyo_same_ipaddr_union()`.

## Control flow

Policy writing first obtains or creates the named `struct tomoyo_group` through `tomoyo_get_group()`, switches `param->list` to the group's member list, parses the member appropriate for the group type, then updates the member list via `tomoyo_update_policy()`. Matching iterates active group members under SRCU, skips deleted entries, and returns on the first pattern/range match.

## State and persistence behavior

Groups persist under `ns->group_list[type]` and each group owns a `member_list`. Group objects and group names are reference-counted shared objects. Path members hold interned path names, number members hold numeric range unions, and address members hold IPv4/IPv6 range unions. Deleted members are marked and later reclaimed by `gc.c`.

## Dependencies and integration points

The file depends on `tomoyo_get_group()` from `memory.c`, `tomoyo_update_policy()` from `domain.c`, name/number/IP parsers, path pattern matching, IP comparison helpers, and SRCU list traversal. File ACLs use path and number groups, network ACLs use address groups and port number groups, and conditions can compare against number/name groups.

## Risks

Group matching is linear in group size, so very large groups can affect hot permission checks. Number group writing intentionally rejects `@` nested groups; address group writing also rejects group indirection, limiting recursion but requiring clear userspace diagnostics. Address comparisons use `memcmp()` over big-endian byte ranges, so parser correctness and IPv4-vs-IPv6 flags are essential. Path group matching returns the matched member path, which can feed wildcard execute transition behavior.

## Test signals

Tests should include member insertion/deletion, duplicate detection, path wildcard matches, numeric overlap edge cases, IPv4 and IPv6 range boundaries, group references from file/network/condition ACLs, deletion while ACLs still reference groups, and performance checks for large groups.
