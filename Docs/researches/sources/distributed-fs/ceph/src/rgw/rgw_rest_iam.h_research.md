# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam.h

## Purpose

`rgw_rest_iam.h` declares shared IAM REST utilities, forwarding helpers, optimistic metadata write retry helpers, and the IAM handler/manager classes.

## Important APIs and Types

The validation helpers enforce IAM limits for policy names, policy ARNs, user names, role names, group names, and paths. `iam_user_arn()` and `iam_group_arn()` format metadata as AWS-style IAM ARNs. `forward_iam_request_to_master()` is the common multisite forwarding function for IAM operations.

`retry_raced_user_write()`, `retry_raced_group_write()`, and `retry_raced_role_write()` wrap atomic read-modify-write loops. They retry up to 10 times on `-ECANCELED`, reload metadata/version trackers, and map persistent races to `-ERR_CONCURRENT_MODIFICATION`.

`RGWHandler_REST_IAM` holds the auth registry and saved POST body, dispatches IAM POST actions, sets IAM protocol flags, and authorizes through S3 auth. `RGWRESTMgr_IAM` returns itself for subresources and creates IAM handlers.

## Control Flow and State

Concrete IAM operations call validation in `init_processing()`, permission helpers in `verify_permission()`, optional master forwarding in `execute()`, and retry helpers around metadata updates. The retry helpers operate on SAL user/group/role objects and their version trackers but do not persist independently.

## Dependencies and Integration Points

The header depends on RGW auth filters, REST, role, SAL, XML, concepts, and `RGWUserInfo`/`RGWGroupInfo`. It is included by IAM role, user, group, policy, OIDC, and account operation implementations.

## Risks and Test Signals

New IAM operations must use the retry helpers for versioned metadata writes or risk exposing raw `-ECANCELED`. The template helpers require invocable lambdas that are safe to repeat after metadata reload. Tests should force store races to verify retry and final 409 mapping, and compile all concrete IAM files against the shared declarations.
