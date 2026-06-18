# sources/distributed-fs/ceph/src/rgw/rgw_rest_user_policy.cc

## Purpose
`rgw_rest_user_policy.cc` implements IAM-style user policy operations for RGW users. It supports inline user policies (`PutUserPolicy`, `GetUserPolicy`, `ListUserPolicies`, `DeleteUserPolicy`) and managed policy attachment operations (`AttachUserPolicy`, `DetachUserPolicy`, `ListAttachedUserPolicies`).

The file bridges IAM query parameters to RGW user attributes, account-aware user lookup, IAM permission evaluation, metadata-master forwarding, and XML IAM responses.

## Important APIs, Types, and Functions
`RGWRestUserPolicy` is the common base. It validates `UserName`, resolves account users by account id and name or tenant users by uid, constructs a user ARN, checks admin caps, and falls back to IAM permission evaluation against that ARN.

`RGWPutUserPolicy` validates `PolicyName` and `PolicyDocument`, parses the policy document, forwards mutating requests to the metadata master when needed, decodes the `RGW_ATTR_USER_POLICY` map, inserts/replaces the inline policy, enforces `rgw_user_policies_max_num`, encodes attrs, and stores the user through `retry_raced_user_write()`.

`RGWGetUserPolicy` and `RGWListUserPolicies` decode `RGW_ATTR_USER_POLICY` and emit one policy or a paginated policy-name list. `RGWDeleteUserPolicy` forwards to the master if needed, removes the inline policy, and treats missing policy as success after successful non-master forwarding.

`RGWAttachUserPolicy_IAM` validates a managed policy ARN, verifies the managed policy exists, forwards to the master if needed, decodes/updates `RGW_ATTR_MANAGED_POLICY`, and stores the user. `RGWDetachUserPolicy_IAM` removes an ARN from that attr. `RGWListAttachedUserPolicies_IAM` lists attached policy ARNs with pagination.

`RGWRestAttachedUserPolicy` rejects managed policy operations unless the authenticated identity belongs to an account, because managed policies are supported only for account users.

Factory functions `make_iam_attach_user_policy_op()`, `make_iam_detach_user_policy_op()`, and `make_iam_list_attached_user_policies_op()` expose these IAM operations to the IAM REST dispatcher.

## Control Flow
Every op first runs `init_processing()`: parse params, identify account-vs-tenant context, load the target user, and compute the target ARN. `verify_permission()` rejects anonymous callers, accepts users with `user-policy` caps, or evaluates IAM action permission against the target user ARN.

Mutating inline and managed policy ops validate input, forward the original IAM request body to the metadata master if this zone is not master, and then update user attrs under `retry_raced_user_write()`. Read/list ops decode attrs and directly emit XML.

Pagination uses `std::map`/`std::set` ordering with `lower_bound(marker)` and `MaxItems` capped at 1000. Truncated responses return the next marker value.

## State and Persistence Behavior
Inline user policies are persisted as an encoded `std::map<std::string, std::string>` in `RGW_ATTR_USER_POLICY` on the user. Managed policy attachments are persisted as encoded `rgw::IAM::ManagedPolicies` in `RGW_ATTR_MANAGED_POLICY`.

All user attr mutations call `user->store_user()` inside `retry_raced_user_write()`, preserving concurrent metadata updates. Mutating requests are forwarded to the metadata master via `forward_iam_request_to_master()` with IAM action/version/user/policy args removed from forwarded args.

Request-local state includes `account_id`, loaded `user`, `user_arn`, policy names/documents, managed policy ARN, marker/max item fields, and the original POST body for forwarding.

## Dependencies and Integration Points
The file depends on IAM validation helpers, managed policy lookup, policy parser, RGW process environment, IAM REST forwarding, SAL user/account APIs, site metadata-master config, RGW user attrs, and IAM XML namespace formatting.

It integrates with `rgw_rest_iam` via factory functions and with account identity through `s->owner.id` and `s->auth.identity->get_account()`.

## Risks
There are subtle sign conventions: some paths assign positive `ERR_NO_SUCH_ENTITY` while most use negative `-ERR_*`. Response/error translation must continue to handle these correctly.

Forwarding strips query args before forwarding. If new required parameters are added and not stripped or preserved correctly, master-zone replay may diverge from local validation.

Managed policies are intentionally limited to account users. Relaxing that check could attach broad account policy semantics to tenant users. Inline policy tenant restriction differs between account and non-account users, so policy parsing must preserve that boundary.

## Test Signals
Tests should cover account user lookup by `UserName`, tenant uid lookup, invalid user/policy names and ARNs, anonymous denial, admin cap allow, IAM permission allow/deny, malformed policy documents, policy count limits, metadata-master forwarding, raced user writes, get/list/delete missing policy behavior, attach unknown managed policy, account-only managed policy enforcement, pagination markers/max items, and decoding errors for corrupted attrs.
