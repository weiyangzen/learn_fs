# sources/distributed-fs/ceph/src/rgw/rgw_acl_swift.h

## Purpose
Declares Swift ACL adapter functions for container headers and account ACL JSON.

## Important APIs, Types, and Functions
- `create_container_policy()` builds policy from Swift read/write header lists.
- `merge_policy()` preserves unchanged read/write sides.
- `format_container_acls()` renders read/write headers.
- `create_account_policy()` and `format_account_acl()` handle `X-Account-Access-Control`.

## Control Flow
No implementation logic is present. The signatures expose ownership, SAL driver, read/write masks, and optional serialized account ACL output.

## State and Persistence
No state is stored. Callers own the `RGWAccessControlPolicy` output and persist it elsewhere.

## Dependencies and Integration Points
Forward-declares ACL and formatter types, includes SAL forward declarations and user owner types, and sits between Swift request handlers and core ACL storage.

## Risks and Edge Cases
The `rw_mask` contract is important: callers must pass it through `merge_policy()` when only one header side is updated. Account ACL formatting can return `std::nullopt`, which callers must treat as no header rather than an empty JSON object.

## Test Signals
Header-level Swift tests should verify declarations match implementation and that request handlers correctly call merge/format helpers.
