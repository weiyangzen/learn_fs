# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_user.h

## Purpose

`rgw_rest_iam_user.h` declares factory functions for IAM user and access-key operations while keeping the concrete operation classes local to `rgw_rest_iam_user.cc`.

## Important APIs

User factories include create, get, update, delete, and list. Access-key factories include create, update, delete, and list. Factories that mutate state accept the POST body so the operation can forward the original IAM request to the metadata master in multisite deployments.

## Control Flow and Integration

The central IAM dispatcher maps AWS `Action` names to these factories. The returned `RGWOp` instances then participate in standard RGW init, permission verification, execution, and response handling.

## Risks and Test Signals

The declarations are part of the action-dispatch ABI inside RGW. Tests should verify that every declared factory is present in `op_generators`, that read-only factories tolerate an unused body, and that mutating factories preserve the body argument for forwarding.
