# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam.cc

## Purpose

`rgw_rest_iam.cc` is the central IAM REST dispatcher and shared IAM utility implementation for RGW. It maps AWS IAM `Action` names to `RGWOp` objects, initializes IAM request handling and S3 authorization, validates IAM names/paths/ARNs, formats IAM user/group ARNs, parses forwarded AWS error responses, and forwards IAM mutations to the metadata master zone in multisite deployments.

## Important APIs and Functions

The `op_generators` map connects IAM actions to constructors from role, user policy, OIDC provider, account, user, and group files. `RGWHandler_REST_IAM::action_exists()`, `op_post()`, `init()`, and `authorize()` implement dispatch and auth. Validation helpers include `validate_iam_policy_name()`, `validate_iam_policy_arn()`, `validate_iam_user_name()`, `validate_iam_role_name()`, `validate_iam_group_name()`, and `validate_iam_path()`.

`iam_user_arn()` and `iam_group_arn()` produce IAM ARNs from RGW metadata. `parse_aws_error_response()` extracts `Code` and `Message` from XML error bodies. `forward_iam_request_to_master()` sends a signed IAM request to the master zonegroup and parses the XML response.

## Control Flow

IAM requests enter through `RGWRESTMgr_IAM::get_handler()`, which constructs `RGWHandler_REST_IAM`. `init()` marks the dialect as `iam` and sets `RGW_REST_IAM`. `authorize()` uses S3 auth. `op_post()` reads `Action`, looks it up in `op_generators`, and constructs the concrete operation, passing the saved post body for operations that may forward to a master zone.

Validation helpers are called by concrete operations during `init_processing()`. Forwarding checks whether the current site has a period and whether it is already the metadata master. If forwarding is required, it locates the master zone, selects a user access key from the authenticated user info, builds an `RGWRESTConn` to master endpoints, calls `forward_iam()`, maps the HTTP status to errno, and parses successful XML into the caller's parser.

## State and Persistence Behavior

This file owns no persistent state. It mutates request state by setting dialect/protocol flags and by removing/rewriting args in concrete callers before forwarding. Persistent changes occur in operations created by the dispatcher or on the master zone reached through forwarding.

## Dependencies and Integration Points

It integrates many IAM submodules: roles, user policies, OIDC providers, groups, users, account summary, REST connections, and zone configuration. It depends on RGW S3 auth, XML parsing, Boost string replacement, regex validation, and SAL site configuration.

## Risks and Edge Cases

The post-body member is copied by value into the handler constructor from a local buffer in `get_handler()`, so it is currently empty unless another layer fills request args independently. Forwarding chooses the first access key in `user.access_keys`; a user without keys may forward with empty credentials, relying on downstream behavior. `validate_iam_policy_arn()` checks length but not full ARN grammar. `validate_iam_path()` requires `/` or a slash-delimited printable path and may reject AWS edge cases.

Forwarded XML has `&quot;` replaced before parsing. Any new forwarded operation must strip consumed args consistently before forwarding, or signatures and action handling can diverge between zones.

## Test Signals

Tests should cover every action name in `op_generators`, unknown/missing `Action`, IAM auth flags, all name/path validation boundaries, ARN formatting for root and non-root users, XML error parsing, non-multisite no-op forwarding, master-zone no-op forwarding, and non-master forwarding with parsed success and error responses.
