# sources/distributed-fs/ceph/src/rgw/rgw_auth.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth.h` defines the core RGW authentication interfaces and identity-applier classes. It separates pure authentication engines from state-mutating appliers and optional completers, and provides concrete identity models for local users, remote users, web identities, assumed roles, service identities, implicit tenants, and anonymous access. The source was read as a complete 996-line header.

## Important APIs, Types, and Functions

`Identity` defines authorization-facing methods such as `get_aclowner()`, `get_perms_from_aclspec()`, `is_admin()`, `is_owner_of()`, `is_root()`, `is_identity()`, identity type, caller ARN, tenant/account accessors, and ops-log writing. `IdentityApplier` extends `Identity` with `load_acct_info()` and `modify_request_state()`. `Completer` represents post-body auth completion. `Engine::AuthResult` models `DENIED`, `GRANTED`, and `REJECTED`, and `Engine` exposes `authenticate()`. `Strategy` stacks engines with `REQUISITE`, `SUFFICIENT`, and `FALLBACK`. Concrete declarations include `WebIdentityApplier`, `ImplicitTenants`, `RemoteApplier`, `LocalApplier`, `RoleApplier`, `ServiceIdentity`, and `AnonymousEngine`.

## Control Flow

The header documents the two-step auth flow: an `Engine` authenticates a request without mutating global/request state, then the granted `IdentityApplier` loads account information and mutates `req_state`; an optional `Completer` validates streaming/message integrity before commit. Factories on applier classes allow protocol-specific engines to create decorated local/remote/web/role appliers without depending on concrete construction code.

## State and Persistence Behavior

Declared state includes user/account metadata, policies, role attributes, token claims, Keystone scope/roles, access key/subuser data, implicit tenant config state, and request-scoped completer/filter state. Persistent writes are not implemented in the header but are declared for appliers that may create or load SAL users/accounts.

## Dependencies and Integration Points

The header depends on Ceph `tl::expected`, function wrappers, `rgw_common`, web identity, Keystone scope, SAL driver/user types through declarations, IAM policy types, principals, ARN, and request state. It is included by S3, Swift, STS, Keystone, registry, and filter code to compose authentication strategies.

## Risks and Edge Cases

The contract relies on engines not mutating state and appliers doing all mutation; breaking that boundary complicates retries and authorization. `AuthResult` intentionally forbids a completer without an applier. Many accessors can throw via implementations, so callers must keep error handling robust. Factories pass ownership-heavy arguments (`unique_ptr`, moved functions, policies), making repeated use after move invalid. Identity matching must maintain compatibility between legacy tenant users and account-based ARNs.

## Test Signals

Interface-level tests should validate `AuthResult` statuses and move behavior, strategy stacking, applier factory construction, and request-state mutation ordering. Integration tests should exercise local/remote/web/role identities through authorization checks, ops log fields, caller identity ARNs, account-aware owner matching, and completer execution before object modification commit.
