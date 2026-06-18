# sources/distributed-fs/ceph/src/rgw/rgw_rest_role.cc

## Purpose

`rgw_rest_role.cc` implements RGW IAM role REST operations: create, delete, get, list, update assume-role policy, inline role policy CRUD/list, role tags, update role metadata, and managed policy attach/detach/list for account roles. It provides operation-level IAM authorization and metadata-master forwarding so role metadata is written consistently across zones.

## Important APIs, types, and functions

- `RGWRestRole::verify_permission()` first evaluates IAM identity/resource permissions with `verify_user_permission()` against the operation action and precomputed role ARN, then falls back to cap-based `RGWRESTOp::verify_permission()`. `check_caps()` checks the `roles` cap with the operation's read/write permission.
- `dump_iam_role()` emits the IAM XML/formatter fields for role responses.
- `parse_tags()` parses AWS query parameters `Tags.member.N.Key` and `Tags.member.N.Value` into a multimap.
- `make_role_arn()` and `load_role()` centralize ARN construction and role lookup. `load_role()` maps missing roles to `-ERR_NO_ROLE_FOUND` and sets the resource ARN once the stored role path is known.
- `check_role_limit()` enforces account `max_roles` by loading account info and counting account roles.
- Concrete operations include `RGWCreateRole`, `RGWDeleteRole`, `RGWGetRole`, `RGWModifyRoleTrustPolicy`, `RGWListRoles`, `RGWPutRolePolicy`, `RGWGetRolePolicy`, `RGWListRolePolicies`, `RGWDeleteRolePolicy`, `RGWTagRole`, `RGWListRoleTags`, `RGWUntagRole`, `RGWUpdateRole`, and internal managed-policy ops.
- Factory functions `make_iam_attach_role_policy_op()`, `make_iam_detach_role_policy_op()`, and `make_iam_list_attached_role_policies_op()` expose managed-policy operations to IAM routing.

## Control flow

Most operations follow a common pattern: parse and validate AWS Query arguments in `init_processing()`, set `account_id` from account identity when present, load role metadata and compute the resource ARN, then execute local or forwarded metadata changes. Write operations check whether the site is metadata master. On secondary zones they call `forward_iam_request_to_master()` with the saved POST body, remove already-parsed parameters from `s->info.args`, parse any needed XML response, and then perform local store/delete with race-tolerant behavior. Metadata mutations use `retry_raced_role_write()` around updates to handle concurrent metadata sync/write races.

`CreateRole` validates role name, path, required trust policy, trust policy parse, description length, tags, tag count, account role limit, and tenant consistency. If forwarded, it decodes `RoleId` and `CreateDate` from the master response so local creation matches master metadata. It maps master-zone duplicate creates to `-ERR_ROLE_EXISTS`, while duplicate after forwarding is treated as success because sync may already have replicated the role.

`DeleteRole` loads the role and, on the master, refuses deletion while inline or managed policies remain. It deletes role metadata and maps already-deleted secondary-zone state to success.

`GetRole` formats stored role info. `ModifyRoleTrustPolicy` validates a required JSON policy document and stores it. `ListRoles` supports `PathPrefix`, `Marker`, and `MaxItems` up to 1000, then lists by account id or tenant and emits truncation metadata.

Inline policy operations validate role and policy names, parse policy JSON with tenant restriction for non-account identities, store policy text in role info, fetch by name with `NoSuchEntity` mapping, list names, and delete policies with idempotent secondary-zone behavior.

Tag operations parse tags or tag keys, load the role, and update stored tag metadata. `UpdateRole` optionally changes description and max session duration, validates duration, and stores role info.

Managed policy operations are supported only for account users. Attach validates `PolicyArn`, confirms the managed policy exists through `rgw::IAM::get_managed_policy()`, inserts the ARN idempotently, and stores. Detach removes the ARN, treating missing policy as success only on secondary zones after forwarding. List emits attached policy ARNs and derives names from the ARN suffix.

## State and persistence behavior

Role metadata is represented by `rgw::sal::RGWRole` and persisted through `create()`, `delete_obj()`, `store_info()`, inline policy helpers, tag helpers, and managed policy fields in `RGWRoleInfo`. Account role quotas are read from account metadata. Most write paths are metadata-master-first in multisite setups and then perform local metadata writes, tolerating races where sync has already applied the master change. Role state includes trust policy, inline permission policy map, managed policy ARN set, tags, description, path, max session duration, creation date, role id, tenant, and account id.

## Dependencies and integration points

The file depends on IAM parsing/evaluation (`rgw_iam_policy`, `rgw_rest_iam`), role validation and storage (`rgw_role.h`, SAL `get_role()`, list/count account roles), account metadata, RGW XML parser/formatter, `forward_iam_request_to_master()`, `retry_raced_role_write()`, `verify_user_permission()`, and standard RGW request state. Factory functions integrate with the broader IAM REST action dispatcher rather than declaring a handler in this file.

## Risks and edge cases

- `parse_tags()` inserts into vectors at `begin() + (index - 1)` without bounds checks. Sparse or out-of-order tag indices can risk invalid iterator behavior.
- Several loops erase matching `Tags.member.*` params while iterating a map with `it++` in the loop header; this pattern can skip entries or invalidate iteration depending on container behavior.
- Many write operations mutate `s->info.args` before forwarding. Any later code that relies on original args must use member copies or POST body.
- `ModifyRoleTrustPolicy` validates with `JSONParser`, while create uses full `rgw::IAM::Policy`; policy validation semantics may differ.
- `RGWUpdateRole::execute()` opens `UpdateRoleResult` and then `ResponseMetadata` inside it, which may not match AWS response nesting expectations.
- Managed policy list declares `RGW_CAP_WRITE` in its base constructor despite being a list/read-style operation, which may be intentional or an authorization bug.
- Secondary-zone idempotence intentionally maps some local missing/existing states to success after successful forwarding; tests must distinguish master and secondary behavior.

## Test signals

Tests should cover role create validation, trust policy parse failures, account role quota, duplicate creates on master and secondary, tenant mismatch, delete conflicts with inline/managed policies, get/list role output and pagination, update assume role policy, inline policy put/get/list/delete including malformed policy and missing policy mappings, tag parse with ordered and malformed indices, tag count limits, untag, update description and session duration validation, managed policy attach/detach/list for account and non-account identities, metadata-master forwarding, sync race idempotence, IAM authorization by action/resource ARN, and fallback role caps.
