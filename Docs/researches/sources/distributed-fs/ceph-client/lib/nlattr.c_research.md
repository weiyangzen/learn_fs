# sources/distributed-fs/ceph-client/lib/nlattr.c

## Purpose
Implements the kernel netlink attribute helper library: validation, parsing, lookup, string/memory copy helpers, and, when `CONFIG_NET` is enabled, skb attribute reservation and emission. It is the common safety layer between netlink family command handlers and untrusted attribute streams.

## APIs, Control Flow, and State
Important exports are `__nla_validate()`, `__nla_parse()`, `nla_policy_len()`, `nla_find()`, `nla_strscpy()`, `nla_strdup()`, `nla_memcpy()`, `nla_memcmp()`, `nla_strcmp()`, `nla_reserve*()`, `nla_put*()`, and `nla_append()`. The core flow is `__nla_validate_parse()`: zero the optional type table, iterate attributes, reject unknown types when strict flags require it, sanitize the type through `array_index_nospec()`, run `validate_nla()`, then store the attribute pointer by type. `validate_nla()` enforces fixed sizes, minimum sizes, nested flags, string termination/length, binary size, ranges, masks, bitfield32 selectors, reject policies, and custom callbacks. Nested policies recurse through `NLA_NESTED` and `NLA_NESTED_ARRAY`, capped by `MAX_POLICY_RECURSION_DEPTH`.

## Dependencies, Integration, Risks, and Tests
Depends on `net/netlink.h`, `skbuff`, ratelimited warnings, nospec helpers, and extack reporting macros. It is integrated by generic netlink families, rtnetlink, and other netlink command parsers. Risks include accepting malformed lengths in non-strict compatibility mode, policy recursion abuse, incorrect nested policy lengths, off-by-one string handling, and skb tailroom miscalculation by callers using unchecked `__nla_*` helpers. Test signals include netlink selftests with strict/non-strict validation, nested-array fuzzing, extack message assertions, attribute range/mask tests, and skb alignment tests for 64-bit attributes.
