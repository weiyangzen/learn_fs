# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_user.cc

## Purpose
This file implements RADOS-backed RGW admin REST operations for users, subusers, access keys, user caps, and user/bucket quotas. It parses `/admin/user` request parameters, enforces user caps, forwards selected metadata changes to the master zone, and delegates persistent updates to user admin operation classes or `RGWUser`.

## Important APIs, Types, And Functions
- `fetch_access_keys_from_master()` forwards a request to the master and decodes returned `RGWUserInfo` keys/create date for non-master user create/modify.
- User operations: `RGWOp_User_List`, `Info`, `Create`, `Modify`, and `Remove`.
- Subuser operations: `RGWOp_Subuser_Create`, `Modify`, and `Remove`.
- Key operations: `RGWOp_Key_Create` and `Remove`.
- Capability operations: `RGWOp_Caps_Add` and `Remove`.
- `UserQuotas`, `RGWOp_Quota_Info`, and `RGWOp_Quota_Set` encode/decode and mutate quota information.
- `RGWHandler_User::{op_get,op_put,op_post,op_delete}` routes subresources to operations.

## Control Flow
GET dispatches to quota info, list, or user info. PUT dispatches to subuser create, key create, caps add, quota set, or user create. POST dispatches to subuser modify or user modify. DELETE dispatches to subuser removal, key removal, caps removal, or user removal. Each operation fills `RGWUserAdminOpState` from REST args and calls the relevant `RGWUserAdminOp_*` method or `RGWUser::modify()`.

User info requires either `uid` or `access-key`; it suppresses keys unless the caller has `users=read`, is a system request, or is admin, while `user-info-without-keys=read` can authorize keyless reads. User create/modify validate that only system users can set the system flag, parse operation masks, key type, placement, storage class, placement tags, account fields, max buckets, suspension, account-root, and generated key flags. On non-meta-master zones, create/modify fetch keys from the master and suppress local generation. Removal, subuser mutations, and cap mutations forward to the master before applying local admin operations. Key create/remove do not use the explicit forwarding path in this file.

Quota info validates `uid` and quota type, initializes `RGWUser`, confirms the user exists, and returns all, user, or bucket quota. Quota set supports JSON body for all quotas or one quota, and HTTP args for one quota type. HTTP-arg mode overlays values on current quota, including `max-size-kb` conversion to bytes, then calls `RGWUser::modify()`.

## State And Persistence Behavior
Persistent user state is held in RGW user metadata through `RGWUserAdminOp_*` and `RGWUser`. Operations can mutate user info, display name, email, access keys, subusers, Swift/S3 key types, caps, suspension, system/account-root flags, account id/path, placement preferences, max bucket limits, and quota fields. Forwarding to the master zone preserves metadata-master authority in multisite deployments; non-master create/modify also import master-generated keys to keep access credentials consistent.

## Dependencies And Integration Points
The file depends on JSON helpers, user admin code, process environment, REST user header, SAL, zone and sysobj services, string-list parsing, op-mask parsing, placement validation, and `rgw_forward_request_to_master()`. It integrates with caps categories `users` and `user-info-without-keys`, with admin identity checks, and with `RGWFormatterFlusher`.

## Risks And Edge Cases
Missing `uid` and `access-key` on user info returns `-EINVAL` to avoid accidentally querying anonymous user. `RGWOp_User_Modify` parses `op-mask` twice, which is redundant and can duplicate validation work. Non-system callers cannot set `system=true`, but other sensitive fields depend on downstream admin validation. Quota HTTP-arg mode cannot set both user and bucket quotas at once without JSON. Forward-to-master failures abort local mutations, but operations that do not forward here rely on lower layers or deployment assumptions. Key visibility is intentionally conditional and must not regress.

## Test Signals
Tests should cover method/subresource dispatch, cap checks including keyless user-info permission, key redaction rules, required uid/access-key validation, system flag rejection for non-system users, op-mask parsing failure, invalid placement rejection, non-master key fetch behavior, master forwarding failures, user/subuser/key/caps CRUD argument mapping, quota JSON and HTTP-arg modes, invalid quota types, missing users, and max-size-kb conversion.
