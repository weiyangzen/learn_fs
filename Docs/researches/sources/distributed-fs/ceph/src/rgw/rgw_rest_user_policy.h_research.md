# sources/distributed-fs/ceph/src/rgw/rgw_rest_user_policy.h

## Purpose
`rgw_rest_user_policy.h` declares IAM user policy operation classes and factory functions used by RGW's IAM REST layer.

## Important APIs, Types, and Functions
`RGWRestUserPolicy` derives from `RGWRESTOp` and stores the IAM action id, required admin cap, account id, loaded SAL user, target user ARN, policy name, user name, and policy document. It declares common parameter parsing, initialization, caps, permission verification, and response handling.

`RGWPutUserPolicy`, `RGWGetUserPolicy`, `RGWListUserPolicies`, and `RGWDeleteUserPolicy` declare inline policy operations and operation type/name overrides. Mutating classes store the POST body for metadata-master forwarding.

The three factory functions expose managed-policy attach/detach/list operations without publishing their concrete implementation classes in the header.

## Control Flow
IAM dispatch code constructs these operations from action names. Common initialization resolves the target user and permissions before each concrete `execute()` reads or mutates policy attrs.

## State and Persistence Behavior
The header declares state needed to persist inline policy maps and managed policy sets in user attrs. Actual encoding/store logic is implemented in the `.cc` file.

## Dependencies and Integration Points
It depends on ARN types, REST base classes, user types, and SAL forward declarations. Integration is through IAM REST action factories and RGW user metadata storage.

## Risks
The base class declares `validate_input()` but this file's implementation does not define/use it in the visible source, so callers should rely on `get_params()`/IAM validation helpers instead. Concrete managed-policy classes are hidden, limiting compile-time coupling but making factory behavior important.

## Test Signals
Build and dispatch tests should ensure IAM action factories return the right operation types, base initialization remains shared, and operation names/types match IAM audit and response expectations.
