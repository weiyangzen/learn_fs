# sources/distributed-fs/ceph/src/rgw/rgw_auth.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth.cc` implements RGW's core authentication strategy and identity-applier behavior. It loads IAM account/group policies, bridges old `RGWUserInfo` auth data to the newer `Identity` interface, sequences auth engines with PAM-like control flags, applies successful auth results to `req_state`, and implements local, remote, web identity, role, implicit-tenant, and anonymous appliers. The source was read as a complete 1386-line implementation.

## Important APIs, Types, and Functions

Important helpers include `match_principal()`, `match_owner()`, `match_account_or_tenant()`, `load_inline_policy()`, `load_managed_policy()`, `load_group_policies()`, and public `load_account_and_policies()`. `transform_old_authinfo()` returns a `tl::expected<std::unique_ptr<Identity>, int>` for legacy callers. Strategy behavior is implemented by `Strategy::authenticate()`, `Strategy::apply()`, and `Strategy::add_engine()`, with helper functions for rejected, denied, and granted engine results. Applier implementations cover `WebIdentityApplier`, `RemoteApplier`, `LocalApplier`, `RoleApplier`, `ImplicitTenants`, and `AnonymousEngine`.

## Control Flow

`Strategy::authenticate()` iterates registered engines in order, catches integer exceptions as denial reasons, and uses `REQUISITE`, `SUFFICIENT`, and `FALLBACK` controls to decide whether to continue. `Strategy::apply()` authenticates, maps special presigned URL errors to request-state errors, loads account info through the granted applier, sets `perm_mask`, lets the applier and optional completer mutate `req_state`, stores identity/completer in `s->auth`, and populates `s->owner`.

Account policy loading first loads account metadata if `RGWUserInfo::account_id` is present, then parses inline and managed user policies, then loads each group and its policies. Missing groups are tolerated as a multisite metadata sync race, while other group-load errors fail the request. Local/remote/web/role appliers implement owner matching, identity matching, ACL permission extraction, request environment population, policy insertion, ops log fields, and lazy account/user creation or loading.

## State and Persistence Behavior

Most state is request-scoped and stored in `req_state`: user, owner, permission mask, auth identity, completer, IAM identity/session policies, environment keys, token claims, and principal tags. `RemoteApplier` and `WebIdentityApplier` can create users in the RGW store using the SAL driver and default quotas. `LocalApplier` transfers ownership of a loaded SAL user exactly once via `user.release()`. `ImplicitTenants` caches config-derived mode and observes config changes. Policies are parsed from user/group/account attrs and kept in memory for authorization.

## Dependencies and Integration Points

The file depends on SAL driver/user APIs, RGW quota defaults, IAM managed/inline policies, Keystone scope structures, RGW logging, request state, principals/ARNs, and Ceph config observation. It is the central integration point between auth engines such as S3, Swift, STS, LDAP/Keystone and later operation authorization (`RGWOp::verify_permissions`) and operation logging.

## Risks and Edge Cases

Principal matching is string/path sensitive and must preserve AWS and legacy tenant semantics. Policy parsing can throw and must not leave partially applied authorization state unnoticed. Remote/web appliers may create users during request authentication, so retries and multisite races matter. `ImplicitTenants` uses `assert(v != IMPLICIT_TENANTS_BAD)` in accessors, making bad config dangerous after recomputation. `LocalApplier::load_acct_info()` consumes the stored user pointer, so repeated calls would return null behavior. Several paths catch `int` exceptions, a Ceph convention that must remain consistent with callers.

## Test Signals

Coverage should include strategy control-flag matrices, deny/reject/grant transitions, special presigned URL error mapping, account and group policy loading including missing group ENOENT, root/admin/owner matching for account and tenant identities, implicit tenant modes for S3 and Swift, local subuser permission masks, remote user creation with default quotas, web identity tag/env insertion limits, role session policy insertion, and anonymous auth setup.
