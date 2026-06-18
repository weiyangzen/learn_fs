# sources/distributed-fs/ceph/src/rgw/rgw_acl_types.h

## Purpose
Defines fundamental serialized RGW ACL-adjacent types and constants shared beyond the RGW process context: permission bits, access keys, subusers, user caps, and ACL grantee/group/permission wrappers.

## Important APIs, Types, and Functions
- Permission constants such as `RGW_PERM_READ`, `RGW_PERM_WRITE`, `RGW_PERM_FULL_CONTROL`, Swift object bits, and `RGW_PERM_INVALID`.
- `RGWAccessKey` and `RGWSubUser` serialized user credential/subuser records.
- `RGWUserCaps` parses, stores, checks, encodes, and dumps admin capability maps.
- `ACLGranteeTypeEnum`, `ACLGroupTypeEnum`, `ACLPermission`, and `ACLGranteeType` provide encoded ACL primitives.

## Control Flow
Inline encode/decode methods use Ceph versioned encoding macros with legacy compatibility. `RGWUserCaps` exposes parsing and checking APIs whose bodies are elsewhere.

## State and Persistence
These types are durable serialized metadata. Numeric enum values and encoded struct versions are persistent wire/storage contracts and must remain stable. `RGWAccessKey` includes active flag and creation date in newer versions while preserving older decodes.

## Dependencies and Integration Points
The header intentionally avoids RADOSGW/OSD-only includes. It depends on common Ceph types and Formatter. It is included by `rgw_basic_types.h` and core ACL/user metadata code.

## Risks and Edge Cases
Changing enum order or permission bit meanings breaks existing metadata. `RGW_PERM_INVALID` is outside normal low-bit permissions and must not be confused with full control. Capability parsing must preserve backward-compatible string forms.

## Test Signals
Encoding compatibility tests, generated-test-instance coverage, cap parsing/removal, active/inactive key JSON decoding, and permission mask behavior are the primary signals.
