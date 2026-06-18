# sources/distributed-fs/ceph/src/rgw/rgw_acl.cc

## Purpose
Implements RGW ACL core behavior: grant registration, permission lookup, public detection, owner emptiness, JSON dumping, equality, and test-instance generation.

## Important APIs, Types, and Functions
- `RGWAccessControlList::add_grant()` inserts grants and updates user/group/referer lookup structures.
- `get_perm()`, `get_group_perm()`, and `get_referer_perm()` compute permissions for identities, public groups, and Swift referer grants.
- `RGWAccessControlPolicy::get_perm()` and `verify_permission()` implement overall permission checks.
- `is_public()` detects grants to AllUsers or AuthenticatedUsers.

## Control Flow
Grant registration maps canonical users and emails into `acl_user_map`, groups into `acl_group_map`, and referers into `referer_list`. Policy permission checks begin with identity ACL-spec permissions, add owner READ_ACP/WRITE_ACP, optionally add public/authenticated group grants, and finally apply referer ACL transformations when a referer string exists and the requested mask is not yet satisfied. `verify_permission()` expands Swift object permission bits into S3-style read/write ACP semantics before comparing against the requested permission and user permission mask.

## State and Persistence
The object state is in encoded ACL/policy types: user/group maps, referer list, grant map, and owner. This file does not persist directly; persistence occurs when containing bucket/object/user metadata encodes these classes.

## Dependencies and Integration Points
Integrates with `rgw::auth::Identity`, ACL types, S3 URI conversion for backward compatibility, formatter JSON encoding, and Swift referer compatibility through `RGW_REFERER_WILDCARD`.

## Risks and Edge Cases
Referer grants are order-sensitive because the last matching referer rewrites `referer_perm`. Email grants are registered in `acl_user_map` by address, which depends on identity ACL-spec behavior. `ACLGrant::generate_test_instances()` appears to set `g1` instead of `g2` for the group sample, which weakens generated test coverage. Public ACL checks intentionally ignore invalid/none values but not all semantic policy combinations.

## Test Signals
Tests should cover owner implicit ACP rights, public ACL ignoring, authenticated versus anonymous identities, referer positive/negative and wildcard behavior, Swift READ_OBJS/WRITE_OBJS conversion, serialization round trips, and generated-test-instance coverage.
