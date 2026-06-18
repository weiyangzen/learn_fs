# sources/distributed-fs/ceph/src/rgw/rgw_rest_account.cc

## Purpose

Implements REST admin account operations for creating, modifying, retrieving, deleting, and setting quotas on RGW accounts.

## Important APIs, Types, and Functions

Defines `RGWOp_Account_Create`, `RGWOp_Account_Modify`, `RGWOp_Account_Get`, `RGWOp_Account_Delete`, and `RGWOp_Account_Quota_Set`, all derived from `RGWRESTOp`. Handler factory methods `RGWHandler_Account::op_post()`, `op_put()`, `op_get()`, and `op_delete()` choose the correct operation.

## Control Flow and Data Flow

Each operation checks `accounts` caps for read or write. Create parses id, tenant, name, email, and max limits. If the local zone is not metadata master, it forwards to the master and uses the master-generated account id from the JSON response before calling `rgw::account::create()`. Modify and delete forward to master first, then parse state and call account modify/remove locally. Get parses selectors and calls `rgw::account::info()`. Quota set requires `id` and `quota-type` of `account` or `bucket`, parses optional max-size, max-objects, and enabled, then calls `rgw::account::modify()`.

## State and Persistence Behavior

Persistent account metadata and quota state are changed by `rgw::account::*` helpers and master-zone forwarding. This file builds `rgw::account::AdminOpState`, handles error mapping such as `-EEXIST` to `-ERR_ACCOUNT_EXISTS`, and streams output through the REST flusher.

## Dependencies and Integration Points

Depends on account admin helpers, process env/site for forwarding, `RESTArgs`, user caps, and SAL driver metadata-master detection. Integrated under the account REST manager and admin API authentication stack.

## Risks and Edge Cases

Modify/delete/quota unconditionally forward to master; behavior on the master depends on `rgw_forward_request_to_master()` semantics. Quota `max-size` is parsed as `int32_t`, which is too narrow for large byte limits despite documentation implying byte sizes. Create uses the forwarded JSON id and fails if it is empty. Optional numeric parsers can leave invalid values as operation errors only if callers inspect returns; these execute methods do not consistently check every `RESTArgs` return.

## Test Signals

Cover caps enforcement, create on master and non-master, generated id propagation, duplicate account mapping, modify/delete forwarding failures, get by id/tenant/name, quota set missing id/type, invalid quota type, large max-size overflow, enabled parsing, and handler method-to-operation selection.
