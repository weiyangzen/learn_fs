# sources/distributed-fs/ceph/src/rgw/rgw_auth_filters.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_filters.h` defines template decorators for `IdentityApplier` objects. They add cross-tenant account override behavior and system-request/impersonation behavior while forwarding the rest of the identity interface to the wrapped applier. The source was read as a complete 374-line header.

## Important APIs, Types, and Functions

`DecoratedApplier<DecorateeT>` is the base forwarding decorator and supports storing either a pointer to an applier or an applier object. `ThirdPartyAccountApplier<T>` overrides `load_acct_info()` for account overrides and is constructed by `add_3rdparty()`. `SysReqApplier<T>` recognizes system users, handles `RGW_SYS_PARAM_PREFIX "uid"` effective owner overrides, marks system requests in `req_state`, supports impersonation, and is constructed by `add_sysreq()`.

## Control Flow

`DecoratedApplier` forwards all identity, account loading, request-state mutation, and ops-log methods to its decoratee. `ThirdPartyAccountApplier::load_acct_info()` uses the wrapped identity's account unless an override exists; if the wrapped identity owns the override it forwards, anonymous requests are scoped to the requested tenant, otherwise it loads the overridden user with legacy tenant compatibility and rejects nonexistent third-party accounts. `SysReqApplier::load_acct_info()` loads the wrapped user, detects `system`, optionally resolves an effective user or account id from system args, and adjusts effective owner/tenant. `SysReqApplier::modify_request_state()` lazily loads system status if needed, marks `args` and `s->system_request`, then forwards mutation.

## State and Persistence Behavior

Decorators keep request-scoped mutable state such as `is_system`, `is_impersonating`, `effective_owner`, and `effective_tenant`. They load users/accounts through the SAL driver but do not create persistent users. `ThirdPartyAccountApplier` may clone loaded users for the selected account.

## Dependencies and Integration Points

The file depends on `rgw_auth.h`, `rgw_common.h`, `driver/rados/rgw_user.h`, Boost tribool, and request HTTP args. It integrates with strategy factories that decorate successful appliers for S3 account overrides, system requests, and admin impersonation.

## Risks and Edge Cases

Template forwarding must preserve value category and pointer/object semantics; misuse can wrap a dangling pointer. `ThirdPartyAccountApplier` uses `null_yield` for user loads, so ASIO contexts can trigger blocking warnings. Anonymous override rewrites user ids in a special way and is tenant-sensitive. `SysReqApplier` trusts system users to request effective owners and throws `-EACCES` on lookup failures. Mutable cached state means repeated calls are stateful.

## Test Signals

Tests should cover pointer and object decoratees, no-override and owned-override paths, third-party nonexistent account rejection, anonymous tenant scoping, system uid and account-id effective-owner overrides, impersonation behavior, `is_admin()` changes for system users, and request-state `system_request` marking.
