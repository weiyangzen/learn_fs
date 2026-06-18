# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_account.h

## Purpose

`rgw_rest_iam_account.h` declares the IAM account-summary operation.

## Important APIs and Types

`RGWGetAccountSummary` derives from `RGWRESTOp`, exposes `verify_permission()`, `execute()`, operation name `get_account_summary`, and op type `RGW_OP_GET_ACCOUNT_SUMMARY`. Its private `add_entry()` helper writes summary map entries.

## Control Flow, State, and Integration

The operation is created by the IAM action dispatcher for `GetAccountSummary`. It uses IAM permissions rather than admin caps and reads account state through the request identity and SAL driver. It does not mutate state.

## Risks and Test Signals

The declaration is narrow. Compile tests should verify the action map can instantiate it, and request tests should verify it is recognized as the expected op type for audit/logging.
