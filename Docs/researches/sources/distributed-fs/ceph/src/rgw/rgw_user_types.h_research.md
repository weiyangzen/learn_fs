# sources/distributed-fs/ceph/src/rgw/rgw_user_types.h

## Purpose
`rgw_user_types.h` defines fundamental serialized RGW owner identity types without depending on full RGW runtime headers.

## Important APIs, Types, and Functions
`rgw_account_id` is a strong typedef over `std::string`. `rgw_user` stores tenant, namespace, and id; supports versioned encode/decode, string conversion/parsing using `$` separators, clear/empty checks, default comparison, Formatter dump, and test instances. `rgw_owner` is a variant of `rgw_user` or `rgw_account_id`. Free functions parse, stringify, stream, and JSON encode/decode owners.

## Control Flow
`rgw_user::to_str()` emits `tenant$id`, `tenant$ns$id`, `$ns$id`, or plain id depending on populated fields. `from_str()` reverses that split.

## State and Persistence Behavior
This is a durable encoding contract. `rgw_user` struct version 2 adds namespace while preserving version 1 decode. `rgw_owner` variant ordering is part of binary compatibility.

## Dependencies and Integration Points
Depends on Formatter, JSON, fmt, strings, variants, and Ceph buffer encoding. Included broadly by RGW user, bucket, account, ACL, and policy code.

## Risks
`rgw_account_id` inherits from `std::string`, which can surprise overload resolution. `$` separator parsing cannot represent ids containing `$` unambiguously. The file warns that variant alternatives cannot be changed or removed.

## Test Signals
Binary compatibility for version 1 and 2 users, string round trips with tenant/ns/id combinations, owner variant JSON round trips, ordering comparisons, and account-id formatting are key.
