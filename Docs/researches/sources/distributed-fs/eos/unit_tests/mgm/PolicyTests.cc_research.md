# sources/distributed-fs/eos/unit_tests/mgm/PolicyTests.cc

## Purpose
Tests MGM policy key construction for read/write traffic policy lookups. It ensures user, group, app, and generic policy keys are generated in the expected priority/order.

## Important APIs, types, and functions
The tests cover `Policy::GetConfigKeys`, `Policy::RWParams`, `RWParams::getKey`, and `RWParams::getKeys`. Constants such as `Policy::gBasePolicyKeys` and read/write markers `:r`/`:w` are verified.

## Control flow
Tests construct `RWParams` with user/group/app and write/read booleans, assert individual derived keys, and verify ordered lookup keys for a base policy such as `policy:bandwidth`.

## State and persistence
No mutable state is kept. The generated keys address MGM configuration entries, so formatting and ordering are compatibility-sensitive.

## Dependencies and integration points
Depends on Google Test, `mgm/policy/Policy.hh`, and MGM constants. It integrates with policy lookup for bandwidth and likely other per-user/group/app controls.

## Risks and test signals
The tests protect key spelling and lookup order. Missing coverage includes empty user/group/app combinations in `getKeys`, escaping of names containing separators, and interactions with real config maps.
