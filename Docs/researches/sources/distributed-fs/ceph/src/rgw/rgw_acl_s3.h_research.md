# sources/distributed-fs/ceph/src/rgw/rgw_acl_s3.h

## Purpose
Declares the S3 ACL adapter API used to translate S3 XML, canned ACLs, and request headers into RGW access control policies.

## Important APIs, Types, and Functions
- `acl_uri_to_group()` and `acl_group_to_uri()` map AWS group URIs to RGW group enums.
- `parse_policy()` parses an S3 `AccessControlPolicy` XML document.
- `write_policy_xml()` serializes a policy as S3 XML.
- `create_canned_acl()` and `create_policy_from_headers()` build policies from request-level ACL inputs.

## Control Flow
The header only declares contracts. The signatures show that parsing and header construction may yield on SAL lookups and may return detailed error messages.

## State and Persistence
No state is stored here. Output state is a caller-owned `RGWAccessControlPolicy`.

## Dependencies and Integration Points
Includes async yield support, RGW XML, shared ACL types, object ownership, SAL forward declarations, and `RGWEnv`.

## Risks and Edge Cases
Callers must pass the correct bucket owner and object ownership mode or S3 ACL semantics can be wrong. `parse_policy()` takes `std::string_view`; callers must keep the backing document alive during parsing.

## Test Signals
API tests should verify all public functions remain available to S3 request handlers and preserve expected error propagation for validation failures.
