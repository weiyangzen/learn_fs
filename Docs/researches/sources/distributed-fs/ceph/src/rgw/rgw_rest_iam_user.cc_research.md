# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_user.cc

## Purpose

`rgw_rest_iam_user.cc` implements IAM user and access-key operations for RGW. It supports user lifecycle, user listing, access key create/update/delete/list, XML response formatting, multisite forwarding for mutations, account quota enforcement, and factory functions for the central IAM action dispatcher.

## Important APIs and Operations

Concrete operations are `RGWCreateUser_IAM`, `RGWGetUser_IAM`, `RGWUpdateUser_IAM`, `RGWDeleteUser_IAM`, `RGWListUsers_IAM`, `RGWCreateAccessKey_IAM`, `RGWUpdateAccessKey_IAM`, `RGWDeleteAccessKey_IAM`, and `RGWListAccessKeys_IAM`. Helpers `make_resource_name()`, `dump_iam_user()`, and `dump_access_key()` format IAM response bodies.

Factories at the bottom expose the operations as `make_iam_create_user_op()`, `make_iam_get_user_op()`, and similar access-key factories.

## Control Flow

User operations derive account id from `s->auth.identity->get_account()`, validate IAM names and paths, load users by account/name through the SAL driver, hide the root user from named user APIs, verify IAM permissions against the target user ARN, and then execute the requested operation.

Create enforces `account.max_users`, generates a UUID user id and tenant, sets create date, optionally forwards to the metadata master to receive the authoritative id, then stores the user exclusively. Get returns either a named user or the signing user when `UserName` is omitted. Update changes path/display name under `retry_raced_user_write()`. Delete optionally forwards, checks on the master that access keys, inline user policies, and managed policies are removed, then removes the user. List streams users with chunked transfer and skips root users.

Access-key operations can target the signing user when `UserName` is omitted. Create enforces account `max_access_keys`, generates key id/secret locally or uses master-forwarded credentials, then stores the key in `RGWUserInfo::access_keys`. Update toggles `active`. Delete erases an access key and treats missing keys as success on non-master after master success. List paginates the user's access-key map and emits `AccessKeyMetadata`.

## State and Persistence Behavior

Persistent state is stored in `RGWUserInfo`: user id, tenant, account id, path, display name, create date, access key map, attrs for policies, and group ids. Mutations use versioned read-modify-write via `retry_raced_user_write()` except exclusive creates and removes. Non-master zones forward mutating IAM requests to the metadata master before applying local state, which keeps generated ids and secrets consistent.

## Dependencies and Integration Points

The file depends on RGW ARN helpers, IAM validation/forwarding/retry helpers, account quota metadata, SAL user/account APIs, access-key generation, policy attr names, managed policy encoding, and formatter output. It integrates with user policy code through `RGW_ATTR_USER_POLICY`, managed policy code through `RGW_ATTR_MANAGED_POLICY`, group code through `group_ids`, and multisite site config through `s->penv.site`.

## Risks and Edge Cases

Forwarding methods strip request args before calling the master; new parameters must be added to strip lists. `RGWCreateAccessKey_IAM::forward_to_master()` checks `if (!user)` instead of the parsed `access_key` XML pointer, which looks like a bug risk around malformed master responses. Delete conflict checks only run on the master; non-master paths rely on master success. List operations use lower-bound markers over maps and can expose ordering differences if key ordering changes.

Quota checks race with concurrent creates but the subsequent metadata write retry narrows only per-user races, not account-wide count races. Access-key create inserts the key before checking `max_keys`; the lambda returns limit exceeded before store, but the in-memory object now contains the extra key for that operation's response path.

## Test Signals

Tests should cover name/path validation, missing account identity, root-user hiding, user quota and access-key quota, master forwarding for creates with returned user id/key secret, update/delete race retries, delete conflict conditions, idempotent access-key update/delete behavior, active/inactive status validation, list pagination, `UserName` omitted behavior for root/account credentials, and malformed forwarded XML handling.
