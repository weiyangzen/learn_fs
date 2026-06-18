# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_account.cc

## Purpose

`rgw_rest_iam_account.cc` implements the IAM `GetAccountSummary` operation. It returns quota and count summary entries for the authenticated account.

## Important APIs and Functions

`RGWGetAccountSummary::verify_permission()` derives the account from `s->auth.identity`, builds the account root ARN with `rgw::account::root_arn()`, and checks `iamGetAccountSummary`. `add_entry()` writes one `SummaryMap` entry with `key` and `value`. `execute()` counts account users and groups when corresponding quotas are finite, then emits XML-like formatter sections for response metadata and summary values.

## Control Flow

The IAM dispatcher constructs this operation for `Action=GetAccountSummary`. Permission verification rejects callers without an authenticated account. Execution reads the authenticated user/account metadata, optionally calls `driver->count_account_users()` and `driver->count_account_groups()`, then writes `Users`, `Groups`, `UsersQuota`, `GroupsQuota`, and `AccessKeysPerUserQuota`.

## State and Persistence Behavior

The operation is read-only. It reads account limits from the identity account and counts users/groups through the SAL driver. No metadata is stored.

## Dependencies and Integration Points

The file depends on account helpers, process environment, IAM permission evaluation, and the SAL driver counting APIs. It integrates with `rgw_rest_iam.cc` through the action map and with account quota enforcement used by user/group creation.

## Risks and Test Signals

Counts remain zero when quotas are unlimited because counting is skipped for negative limits. That may be intentional for cost but can surprise clients expecting current counts. Tests should cover permission denial, no account identity, finite and unlimited quotas, count-driver failures, and response keys.
