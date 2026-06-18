# sources/distributed-fs/ceph/src/rgw/rgw_acl.h

## Purpose
Defines the core RGW ACL data model: grant variants, referer grants, access control lists, owners, and access control policies.

## Important APIs, Types, and Functions
- `ACLGrant` wraps canonical user, email, group, unknown, or referer grantees plus `ACLPermission`.
- `ACLReferer` parses HTTP referer hosts and matches wildcard/domain rules.
- `RGWAccessControlList` stores grant maps and accelerated permission maps.
- `ACLOwner` supports user or account owners through `rgw_owner`.
- `RGWAccessControlPolicy` combines owner and ACL and exposes permission verification.

## Control Flow
Most methods are inline encode/decode helpers and simple builders. Decode paths preserve legacy compatibility, reconstructing grantee variants from encoded type and fields. `create_default()` grants full control to the owner and sets owner identity/display name. `ACLReferer::is_match()` extracts host from a URL, supports `*`, exact host, and suffix matches for leading-dot specs.

## State and Persistence
These are serialized metadata types. Encoders use versioned Ceph encoding macros; the numeric values of grantee and group enums are encoded and must not change. ACL maps and referer lists are stored with the policy when bucket/object metadata persists ACLs.

## Dependencies and Integration Points
Depends on `rgw_basic_types.h`, `include/types.h`, Boost optional/string predicates, and `rgw::auth::Identity` in method contracts. S3 and Swift adapters construct these shared types.

## Risks and Edge Cases
Variant index order is tied to `ACLGranteeTypeEnum`; reordering the variant or enum breaks decoding semantics. Referer host parsing rejects malformed URLs but has minimal normalization. `remove_canon_user_grant()` erases grants by owner string and does not affect group/referer grants.

## Test Signals
Round-trip encode/decode tests across legacy versions, referer URL parsing, default policy creation, owner account/user variants, and grant-map registration consistency are key signals.
