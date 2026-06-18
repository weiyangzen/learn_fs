# sources/distributed-fs/ceph/src/rgw/rgw_rest_role.h

## Purpose

`rgw_rest_role.h` declares the IAM role operation classes implemented in `rgw_rest_role.cc`. It defines a shared authorization base, one class per IAM role action, and factories for managed policy role actions consumed by the broader IAM REST dispatcher.

## Important APIs, types, and functions

- `RGWRestRole` derives from `RGWRESTOp` and stores the IAM action id and cap permission required by a concrete action. It also stores `account_id` and a `rgw::ARN resource` that must be initialized before permission verification. It overrides `check_caps()` and `verify_permission()`.
- Role lifecycle operations: `RGWCreateRole`, `RGWDeleteRole`, `RGWGetRole`, `RGWListRoles`, and `RGWUpdateRole`.
- Trust policy operation: `RGWModifyRoleTrustPolicy`.
- Inline policy operations: `RGWPutRolePolicy`, `RGWGetRolePolicy`, `RGWListRolePolicies`, and `RGWDeleteRolePolicy`.
- Tag operations: `RGWTagRole`, `RGWListRoleTags`, and `RGWUntagRole`.
- Managed-policy factories: `make_iam_attach_role_policy_op()`, `make_iam_detach_role_policy_op()`, and `make_iam_list_attached_role_policies_op()`.

Each concrete class declares `init_processing()`, `execute()`, `name()`, and `get_type()`, and stores request-scoped parsed parameters and loaded role pointers where needed.

## Control flow

The broader IAM REST routing layer constructs these operation classes based on AWS IAM `Action` names. During request processing, `init_processing()` parses role-specific arguments and usually initializes `resource`; `RGWRestRole::verify_permission()` evaluates IAM permissions against `action` and `resource`; and `execute()` performs the role operation and writes an IAM XML-style response. Write operations that need original form data store `bufferlist bl_post_body` for metadata-master forwarding.

## State and persistence behavior

The header defines only request-scoped state: role names, policy names/documents, tags, untag vectors, optional description, max session duration, loaded `rgw::sal::RGWRole` pointers, and POST bodies. Persistent role state is written by the `.cc` implementation through SAL role objects. The `account_id` and `resource` members are central to authorization and account-scoped storage.

## Dependencies and integration points

The header depends on Boost optional, async yield context, `rgw_arn.h`, `rgw_role.h`, and `rgw_rest.h`. It exposes operation types such as `RGW_OP_CREATE_ROLE`, `RGW_OP_DELETE_ROLE`, and policy/tag operation ids for logging, tracing, and RGW operation accounting. The managed-policy factory functions are an integration boundary with IAM action dispatch without exposing the internal classes in the header.

## Risks and edge cases

- The comment on `resource` is important: if a derived class fails to initialize it before `verify_permission()`, IAM authorization may evaluate the wrong ARN.
- Several write classes hold `bufferlist` copies of the POST body; callers should pass the body consistently or forwarding will be incomplete.
- The header uses `boost::optional` for `RGWUpdateRole::description` while other code may prefer `std::optional`, reflecting existing codebase style but worth noting for future changes.
- Loaded `role` pointers are unique ownership and request-scoped. Execute paths assume `init_processing()` successfully populated them.

## Test signals

Construction/routing tests should verify every IAM role action maps to the expected class and `RGWOpType`, each operation name is stable for logging/admin ops, read actions use read caps and write actions use write caps, managed-policy factories return usable ops, and permission verification sees initialized account/resource state for create, list, loaded-role, and managed-policy paths.
