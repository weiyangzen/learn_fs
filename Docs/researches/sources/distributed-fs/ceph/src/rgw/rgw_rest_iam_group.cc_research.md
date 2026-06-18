# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_group.cc

## Purpose

`rgw_rest_iam_group.cc` implements IAM group operations for RGW: create/get/update/delete/list groups, add/remove/list group users, inline group policies, managed policy attachments, and factory functions used by the IAM dispatcher.

## Important APIs and Operations

The file defines concrete `RGWOp` classes for `CreateGroup`, `GetGroup`, `UpdateGroup`, `DeleteGroup`, `ListGroups`, `AddUserToGroup`, `RemoveUserFromGroup`, `ListGroupsForUser`, `PutGroupPolicy`, `GetGroupPolicy`, `DeleteGroupPolicy`, `ListGroupPolicies`, `AttachGroupPolicy`, `DetachGroupPolicy`, and `ListAttachedGroupPolicies`. Helpers `make_resource_name()`, `dump_iam_group()`, and local `dump_iam_user()` produce response fields.

At the bottom, factory functions such as `make_iam_create_group_op()` expose these classes to `rgw_rest_iam.cc`.

## Control Flow

Each operation follows the same pattern: `init_processing()` derives account id from the authenticated identity, validates required names, paths, policy names, policy ARNs, markers, or max items, and loads group/user metadata through the SAL driver. `verify_permission()` builds an IAM ARN for the group or user and checks the specific IAM action. Mutation operations forward to the metadata master when `site.is_meta_master()` is false, then apply local changes.

Create checks the account's `max_groups` quota, generates a UUID group id and tenant, optionally forwards to master to reuse the master-generated id, and stores the group exclusively. Update uses `retry_raced_group_write()` to change path/name. Delete verifies on the master that inline policies, managed policies, and users are removed before deleting. Membership operations update `RGWUserInfo::group_ids` through `retry_raced_user_write()`. Listing operations stream or format IAM XML response sections with truncation markers.

Inline policies are stored in group attrs under `RGW_ATTR_IAM_POLICY` as an encoded map of policy name to document. Managed policy ARNs are stored under `RGW_ATTR_MANAGED_POLICY` as `rgw::IAM::ManagedPolicies`.

## State and Persistence Behavior

Persistent state is group metadata (`RGWGroupInfo`), group attrs, object version trackers, user `group_ids`, and account group counts. Writes use exclusive create or versioned read-modify-write with retry on `-ECANCELED`. Non-master zones forward mutating IAM calls to the master before applying local mirrored updates, and they treat some missing deletes as success if the master already succeeded.

## Dependencies and Integration Points

This file depends on RGW ARN formatting, IAM policy parsing and managed-policy lookup, SAL group/user/account APIs, process environment site config, the shared IAM validation/forwarding helpers, and formatter XML output. It integrates with account quota settings and with user metadata because group membership is stored on users.

## Risks and Edge Cases

Deletion conflict checks depend on decoding attr blobs; corrupt policy attrs return `-EIO`. Managed policy attach validates the policy ARN against built-in managed policies but the ARN grammar check itself is light. Some log/error messages say "user policies" in group paths, which can mislead debugging. `CreateGroup` logs account load failure but does not immediately return before inspecting `account.max_groups`, which is a risk if the account load failed. Membership updates only store group ids on users, so list/group queries depend on SAL indexes honoring that model.

Pagination uses map/set ordering and marker lower bounds; marker semantics should be kept stable for AWS compatibility. Forwarding strips consumed args before sending to the master, so any new request parameter must be handled consistently.

## Test Signals

Tests should cover all required parameter validation, path/name constraints, quota exceedance, IAM permission denial, create/update/delete forwarding, concurrent update retries, delete conflicts for users/inline/managed policies, idempotent add/remove membership, inline policy parse errors and 100-policy limit, managed policy attach/detach/list, pagination markers, and root/account identity edge cases.
