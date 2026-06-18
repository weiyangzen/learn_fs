# sources/distributed-fs/ceph/src/rgw/rgw_acl_swift.cc

## Purpose
Implements Swift container and account ACL conversion to/from RGW's shared ACL model, including Swift referrer ACL syntax and account ACL JSON.

## Important APIs, Types, and Functions
- `create_container_policy()` parses `X-Container-Read` and `X-Container-Write` lists.
- `merge_policy()` preserves old read/write grants when only one side is updated.
- `format_container_acls()` renders policy grants back into Swift header strings.
- `create_account_policy()` parses `X-Account-Access-Control` JSON arrays for admin/read-write/read-only.
- `format_account_acl()` serializes account grants back to Swift account ACL JSON.

## Control Flow
Container policy creation starts from a default owner-full-control policy, splits read/write lists on spaces and commas, parses each grant as a user or `.r` referrer spec, and updates an `rw_mask` to record which ACL sides were supplied. Referrer grants may be positive or negative and are rejected for write ACLs. Account policy creation parses JSON arrays and adds grants with full-control, read/write, or read-only permissions. Formatting walks the grant map and partitions grants by Swift semantics.

## State and Persistence
This file only constructs and formats `RGWAccessControlPolicy`. Durable state is stored by the calling bucket/account metadata paths. It does load user records through SAL to set canonical ids and display names.

## Dependencies and Integration Points
Depends on Swift header semantics, RGW JSON parser, shared ACL types, SAL user loading, and public group compatibility (`.r:*` maps to AllUsers).

## Risks and Edge Cases
`user_to_grant()` silently creates a canonical grant even when user loading fails, using the requested id with an empty display name. Negative referer grants depend on order-preserving `referer_list` handling in core ACL checks. Formatting cannot represent every possible RGW ACL and skips unsupported entries. `uid_is_public()` indexes the first two chars without checking length, so malformed empty/short strings could be risky if passed.

## Test Signals
Tests should cover `.r:*`, exact/suffix/negative referers, write-referrer rejection, partial read/write updates via `merge_policy()`, account ACL JSON categories, missing users, and format/parse round trips.
