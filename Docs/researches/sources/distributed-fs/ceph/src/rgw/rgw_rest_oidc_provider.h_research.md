# sources/distributed-fs/ceph/src/rgw/rgw_rest_oidc_provider.h

## Purpose

`rgw_rest_oidc_provider.h` declares IAM OIDC provider operation classes used by the central IAM dispatcher.

## Important APIs and Types

`RGWRestOIDCProvider` is the common base carrying the IAM action id, admin cap permission, and target ARN resource used by `verify_permission()`. Derived classes represent create, delete, get, list, add client id, remove client id, and update thumbprint operations. Mutating operations store the original POST body for master-zone forwarding. Each class declares `init_processing()` where request parsing is needed, `execute()`, operation name, and `RGWOpType`.

## Control Flow and State

The dispatcher constructs these classes by action name. `init_processing()` must initialize the protected `resource` before permission verification. Execution then uses SAL OIDC provider APIs and optional master forwarding. Per-operation members store parsed URL, client id, thumbprints, or provider info.

## Dependencies and Integration Points

The header depends on ARN support, RGW REST base classes, and `RGWOIDCProviderInfo`. It integrates with `rgw_rest_iam.cc`, IAM permission checks, and SAL provider persistence.

## Risks and Test Signals

The base class permission flow depends on derived classes setting `resource` early. Missing that initialization can evaluate permissions against an empty ARN or fall back to broad caps. Tests should exercise init-before-verify ordering for every OIDC action and verify op type mappings for audit/logging.
