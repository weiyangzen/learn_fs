# sources/distributed-fs/ceph/src/rgw/rgw_acl_s3.cc

## Purpose
Implements S3 ACL XML parsing/serialization, canned ACL construction, and `x-amz-grant-*` header parsing for RGW's shared ACL model.

## Important APIs, Types, and Functions
- XML object classes parse `AccessControlPolicy`, `Owner`, `Grant`, `Grantee`, `Permission`, `ID`, `URI`, and `EmailAddress`.
- `read_owner_display_name()` resolves user or account owners through SAL.
- `resolve_grant()` validates canonical user ids, email users, and group URIs.
- Namespace exports: `acl_uri_to_group()`, `acl_group_to_uri()`, `parse_policy()`, `write_policy_xml()`, `create_canned_acl()`, and `create_policy_from_headers()`.

## Control Flow
S3 XML parsing builds an XML object tree, validates required owner and ACL elements, resolves the owner against SAL, then converts each grant into a canonical/group ACLGrant. Header parsing walks known grant headers, splits comma-separated grantees, parses key/value forms (`emailAddress=`, `id=`, `uri=`), resolves external identifiers, and adds grants. Canned ACL creation always grants object owner full control, optionally grants public/authenticated users or bucket owner, and handles ObjectOwnership overrides.

## State and Persistence
The file constructs in-memory `RGWAccessControlPolicy` objects. Persistence happens later when bucket/object metadata stores the policy. Reads against SAL validate and enrich grantees with display names, but this file does not write metadata directly.

## Dependencies and Integration Points
Depends on RGW XML parser classes, SAL user/account lookup, S3 error codes, `RGWEnv` request headers, object ownership settings, and the shared ACL types.

## Risks and Edge Cases
Email grantees require lookup and may return S3-specific unresolved-email errors. `BucketOwnerEnforced` rejects most ACLs and rewrites owner to the bucket owner. XML serialization omits non-S3-compatible permission bits. Header splitting is comma-based and assumes grantee value parsing handles quoted values correctly.

## Test Signals
Tests should cover all canned ACLs, ObjectOwnership modes, XML owner/grant validation, email/canonical/group grant resolution failures, header parsing for each permission, XML round trips, and non-S3 permission filtering in output.
