# subset-b-006984 Research

Grouped source research for the Ceph RGW Beast/Boost.Asio frontend, ASIO blocking diagnostics, core authentication abstractions, decorator filters, Keystone auth engines, auth strategy registry, and S3 signature helpers. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.cc` implements RGW's Boost.Asio/Beast HTTP frontend behind the public `RGWAsioFrontend` wrapper. It configures TCP and SSL listeners, accepts client sockets, parses HTTP requests, adapts Beast streams into RGW's `ClientIO`/`RGWRestfulIO`, dispatches `process_request()`, logs access records, supports pause/unpause for dynamic config reload, and shuts down listeners/connections. The source was read as a complete 1411-line implementation.

## Important APIs, Types, and Functions

Important local types are `RGWAsioBackoff`, `StreamIO<Stream>`, `Connection`, `ConnectionList`, and private `AsioFrontend`. `StreamIO` implements `write_data()` and `recv_body()` around Beast read/write and timeout handling. `handle_connection()` is the per-connection request loop. `AsioFrontend::init()` parses frontend configuration and starts accept coroutines. SSL builds are centered on `ssl_init()`, `ssl_reload()`, `ssl_reload_timer_start()`, `ssl_set_private_key()`, and `ssl_set_certificate_chain()`. Socket lifecycle is driven by `accept()`, `on_accept()`, `stop()`, `join()`, `pause()`, and `unpause()`. The public `RGWAsioFrontend` methods simply delegate to `Impl`.

## Control Flow

Initialization reads `prefix`, `request_timeout_ms`, `max_header_size`, TCP/SSL ports/endpoints, `tcp_nodelay`, `so_reuseport`, and backlog options. It opens acceptors, applies IPv6-only and reuse options, binds/listens, spawns one accept coroutine per listener, and finally drops privileges. `accept()` loops on `async_accept()`, backs off on resource exhaustion, and hands accepted sockets to `on_accept()`. `on_accept()` spawns a strand-bound coroutine per connection; SSL listeners perform a timed server handshake before entering `handle_connection()`.

`handle_connection()` repeatedly creates a Beast parser, reads headers under `timeout_timer`, obtains a shared pause lock, constructs `RGWRequest`, extracts endpoints, wraps the stream in buffering/chunking/content-length/reordering filters, and calls `process_request()`. It emits an access log entry when enabled, checks `StreamIO` for fatal transport errors, honors keep-alive, and discards unread body bytes before the next request. Bad headers receive a 400 response; reset/abort/end-of-stream exits quietly.

## State and Persistence Behavior

The frontend owns in-memory listener state, an intrusive list of live `Connection` objects, pause/shutdown flags, timeout/header-limit configuration, optional dmClock scheduler, and optional shared SSL context. There is no direct file persistence. SSL material may be loaded from filesystem paths or from RGW config-key storage via `config://`. Runtime SSL reload swaps the shared context atomically where supported and keeps existing connections on their previous context. Pause and graceful stop coordinate outstanding requests with `SharedMutex`.

## Dependencies and Integration Points

The file depends on Boost.Asio, Boost.Beast HTTP parsers, optional OpenSSL, Ceph clocks/logging/config parsing, RGW SAL driver services, zone metadata expansion, `rgw_asio_client`, `rgw_dmclock_async_scheduler`, and `rgw_asio_frontend_timer`. The major integration point is `process_request(env, req, uri_prefix, client, optional_yield, scheduler, ...)`, which connects accepted HTTP traffic to the RGW REST operation stack. ASIO coroutine execution interacts with `rgw_asio_thread` warnings through `is_asio_thread` checks in stop paths and async-yield choices.

## Risks and Edge Cases

Header size is capped by the fixed 64 KiB parse buffer; invalid configured values are warned and defaulted or capped. The `SO_REUSEADDR | SO_REUSEPORT` `setsockopt()` call uses a bitwise OR as the option name, which is platform-sensitive. SSL reload failure keeps the old context but repeated bad config logs periodically. Timeout handlers cancel and shut down sockets asynchronously, so connection lifetime relies on intrusive references. `std::localtime()` in access logging is process-global and may be a concurrency concern. `pause()` cancels accept loops and optionally closes active connections depending on graceful-stop config. Errors after partial request processing can break keep-alive and stop the loop.

## Test Signals

Useful tests include endpoint parsing for IPv4, IPv6 bracket syntax, default ports, bad ports, and oversized header limits; listener bind smoke tests with and without SSL; request timeout tests for header, body, write, and SSL handshake paths; keep-alive tests with unread body discard; graceful pause/unpause tests under active requests; SSL config-key and file loading tests including reload failure retention; resource-limit accept backoff tests; and access-log assertions for method, target, HTTP version, byte counts, TLS metadata, and latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.h` declares the public RGW frontend class for the Boost.Asio/Beast implementation. It exposes the standard `RGWFrontend` lifecycle while hiding implementation details behind a private `Impl` pointer. The source was read as a complete 29-line header.

## Important APIs, Types, and Functions

The key type is `RGWAsioFrontend : public RGWFrontend`. It declares a constructor accepting `RGWProcessEnv`, `RGWFrontendConfig`, dmClock scheduler context, and an `io_context`, plus `init()`, `run()`, `stop()`, `join()`, `pause_for_new_config()`, and `unpause_with_new_config()`. `REQUEST_TIMEOUT` is defined as `65000` milliseconds and is used by the implementation as the default request timeout.

## Control Flow

This header contains no executable control flow. Runtime behavior is implemented in `rgw_asio_frontend.cc`; callers interact with the object through the `RGWFrontend` virtual interface.

## State and Persistence Behavior

The only member is `std::unique_ptr<Impl> impl`, which owns all listener, socket, scheduler, SSL, and pause state in the implementation file. No persistent storage is declared here.

## Dependencies and Integration Points

The header includes Boost.Asio `io_context` and `rgw_frontend.h`. It is the construction-time bridge between RGW frontend selection code and the Beast/Asio implementation.

## Risks and Edge Cases

The PIMPL boundary keeps compile dependencies low but means lifecycle correctness depends on the implementation honoring `RGWFrontend` expectations. The macro-style `REQUEST_TIMEOUT` is globally visible after inclusion and could collide with another macro.

## Test Signals

Compile/link coverage should verify construction through frontend factories, virtual lifecycle dispatch, and pause/unpause calls during config reload. ABI-sensitive tests should ensure the header remains compatible with `RGWFrontend` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend_timer.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend_timer.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend_timer.h` provides a small generic timeout wrapper for stream operations in the ASIO frontend. It starts a waitable timer and cancels/shuts down the stream socket if the timer expires. The source was read as a complete 66-line header.

## Important APIs, Types, and Functions

`rgw::timeout_handler<Stream>` stores an intrusive reference to the stream/connection owner and calls `get_socket().cancel()` and `shutdown()` when the wait completes without cancellation. `rgw::basic_timeout_timer<Clock, Executor, Stream>` wraps `boost::asio::basic_waitable_timer`, stores the timeout duration and intrusive stream pointer, and exposes `start()` and `cancel()`.

## Control Flow

Callers construct a timer with an executor, duration, and stream reference. `start()` arms the timer only when the duration is positive. If the async wait fires normally, `timeout_handler` cancels and shuts down the underlying TCP socket. `cancel()` cancels the wait after successful I/O so the handler receives an operation-aborted error and does not close the socket.

## State and Persistence Behavior

State is entirely in memory: timer object, duration, and an intrusive reference that keeps the stream owner alive until the wait handler finishes. There is no persistent state.

## Dependencies and Integration Points

The header depends on Boost.Asio timers, intrusive pointers, Ceph time types, and a stream type exposing `get_socket()`. `rgw_asio_frontend.cc` instantiates it with `ceph::coarse_mono_clock`, `any_io_executor`, and `Connection`.

## Risks and Edge Cases

Timeout closure is intentionally forceful and may race with normal stream shutdown, so errors are ignored during shutdown. If callers forget `cancel()` after successful I/O, the timer can close an otherwise healthy socket. If duration is zero or negative, both `start()` and `cancel()` become no-ops, disabling timeout protection.

## Test Signals

Tests should cover positive and zero-duration timers, cancellation before expiry, expiry-triggered socket cancellation, and lifetime safety when the owning connection would otherwise be destroyed before the handler runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_thread.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_asio_thread.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_asio_thread.cc` implements diagnostics for synchronous/blocking librados calls made from ASIO frontend threads. The source was read as a complete 40-line file.

## Important APIs, Types, and Functions

It defines `thread_local bool is_asio_thread = false` and `maybe_warn_about_blocking(const DoutPrefixProvider*)`. When called on an ASIO-marked thread, it asserts if `rgw_asio_assert_yielding` is enabled, otherwise logs a warning and optionally a backtrace when `_BACKTRACE_LOGGING` is built.

## Control Flow

Callers mark an ASIO execution scope through the RAII helper declared in the header. `maybe_warn_about_blocking()` returns immediately when the current thread is not marked. On marked threads, it reads config from the `DoutPrefixProvider`, performs an always assertion for strict validation mode, and logs diagnostic output.

## State and Persistence Behavior

The only state is thread-local `is_asio_thread`. It is not persisted and is scoped by caller discipline.

## Dependencies and Integration Points

The implementation depends on Ceph logging, assertions, `DoutPrefixProvider`, and optional `ClibBackTrace`. It integrates with code paths that accept `optional_yield`: when no yield is available and a blocking call is about to happen, those paths can call this helper to detect bad ASIO usage.

## Risks and Edge Cases

The function assumes `dpp` is non-null. Strict mode uses `ceph_assert_always`, so a blocking call on an ASIO thread can terminate the process in validation configurations. Backtrace logging may be noisy at high request rates.

## Test Signals

Unit tests can toggle `is_asio_thread` and `rgw_asio_assert_yielding` to verify no-op, warning, and assertion behavior. Integration tests should ensure asynchronous request paths pass yields to librados rather than triggering this warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_thread.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_thread.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_asio_thread.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_asio_thread.h` declares the ASIO-thread blocking-call diagnostic state and RAII marker. The source was read as a complete 39-line header.

## Important APIs, Types, and Functions

The header declares `extern thread_local bool is_asio_thread`, `maybe_warn_about_blocking(const DoutPrefixProvider*)`, and `warn_about_blocking_in_scope`. The RAII constructor asserts the thread was not already marked and sets `is_asio_thread = true`; the destructor resets it to false.

## Control Flow

Code running inside `boost::asio::io_context::run()` can place `warn_about_blocking_in_scope` on the stack. Nested scopes are forbidden by assertion. Any lower-level blocking-sensitive code can call `maybe_warn_about_blocking()` to emit diagnostics.

## State and Persistence Behavior

The header exposes thread-local transient state only. The RAII helper relies on lexical scope to restore the flag.

## Dependencies and Integration Points

It depends on `assert.h` and forward-declares `DoutPrefixProvider`. It is included by the ASIO frontend and lower RGW paths that need to detect blocking behavior.

## Risks and Edge Cases

Nested marker scopes assert, so callers must know whether they are already inside an ASIO-marked region. If a scope is bypassed by abnormal termination, the thread-local flag may remain stale until thread exit, though normal C++ stack unwinding handles exceptions.

## Test Signals

Compile tests should cover inclusion without heavy RGW dependencies. Runtime tests should verify RAII set/reset behavior and nested assertion behavior in debug configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_filters.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_filters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.cc` implements Keystone token authentication and Keystone-backed S3/EC2 authentication for RGW. It validates Keystone tokens, service tokens, EC2 credentials, maps Keystone roles/scopes into RGW remote auth info, and maintains an access-key secret cache for Keystone S3 auth. The source was read as a complete 833-line implementation.

## Important APIs, Types, and Functions

`TokenEngine::is_applicable()`, `get_from_keystone()`, `get_acl_strategy()`, `get_creds_info()`, and `authenticate()` handle token auth. `EC2Engine::get_from_keystone()`, `get_secret_from_keystone()`, `get_access_token()`, `get_acl_strategy()`, `get_creds_info()`, and `authenticate()` handle S3 token/secret validation. `SecretCache::find()` and `SecretCache::add()` implement LRU/TTL caching of Keystone token envelopes and secrets.

## Control Flow

Token auth rejects empty tokens or missing Keystone URL, checks token cache by token id, optionally validates a service token to allow expired user tokens, validates the user token through Keystone `v3/auth/tokens`, updates role flags, checks expiration and accepted roles, caches the envelope, and grants a `RemoteApplier`. Admin-token 401 responses invalidate and retry the admin token cache once.

EC2 auth tries `SecretCache` first and verifies the request signature locally when a secret is cached. On miss or mismatch it posts to Keystone `v3/s3tokens`, fetches the EC2 secret from `/v3/users/{id}/credentials/OS-EC2/{access}`, caches token/secret pairs, checks token expiration and accepted roles, and grants a remote applier plus an S3 completer factory. Signature mismatch for a known Keystone access key is a hard reject to prevent fallback to other engines.

## State and Persistence Behavior

The implementation uses Keystone admin token cache through `rgw::keystone::TokenCache`, the singleton `SecretCache` for EC2 token/secret pairs, and SAL-backed remote appliers for later user/account loading or creation. `SecretCache` holds a map and LRU list under a mutex, expires entries by token expiration or configured TTL, and trims to `rgw_keystone_token_cache_size`.

## Dependencies and Integration Points

Dependencies include Keystone service HTTP transceivers, JSON parser/formatter, Base64 helpers, Ceph crypto/signature helpers through S3 engine interfaces, RGW Keystone config and scope logging, token cache, accepted role config, and `rgw_auth_s3` abstract AWS engine APIs. The file bridges external Keystone identity into RGW's remote auth and S3 completer flow.

## Risks and Edge Cases

Admin-token invalidation/retry must avoid infinite loops. Service token handling intentionally permits expired user tokens for a bounded cache duration, so role and TTL configuration are security-sensitive. EC2 cache mismatch falls back to Keystone and may reject rather than deny when access key exists but signature is wrong. JSON parsing failures and missing credential fields return `-EINVAL`. `SecretCache` stores secrets in memory and must respect TTL/size limits. OPTIONS CORS requests intentionally ignore signature validation in one path.

## Test Signals

Tests should cover token cache hit/miss, admin-token 401 invalidation, service token role checks, expired-token behavior with and without service token, accepted/admin/reader role mapping, Keystone 404/401/error status mapping, EC2 cache hit with valid and invalid signatures, secret fetch JSON errors, LRU eviction and TTL expiry, CORS ignore-signature path, and reject-vs-deny behavior for signature mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.h` declares Keystone-specific RGW auth engines and the Keystone S3 secret cache. It separates token-based Keystone auth from EC2/S3-token auth while both produce RGW remote appliers. The source was read as a complete 210-line header.

## Important APIs, Types, and Functions

`rgw::auth::keystone::TokenEngine` derives from `Engine` and owns token extractors, a remote applier factory, Keystone config, and token cache. `SecretCache` is a singleton cache of token envelopes and secret strings with `find()` and `add()`. `EC2Engine` derives from `rgw::auth::s3::AWSEngine`, owns a remote applier factory, Keystone config/token cache, and `SecretCache`, and overrides the AWS auth path with Keystone-backed secret lookup.

## Control Flow

The declarations show token auth extracting auth and service tokens from `req_state`, then delegating to private helpers. EC2 auth accepts access key, signature, session token, string-to-sign, signature factory, completer factory, and request state from the S3 AWS engine abstraction, then uses Keystone helpers to obtain a token/secret and return a granted remote applier with completer.

## State and Persistence Behavior

`TokenEngine` and `EC2Engine` hold references to long-lived Keystone config and token cache objects. `SecretCache` owns an in-memory map, LRU list, mutex, maximum size, and TTL derived from Ceph config. No persistent data is stored by this header itself.

## Dependencies and Integration Points

The header depends on `rgw_auth.h`, `rgw_auth_s3.h`, `rgw_rest_s3.h`, `rgw_common.h`, and `rgw_keystone.h`. It is used by authentication registry/strategy construction when Keystone is enabled.

## Risks and Edge Cases

The singleton `SecretCache` captures `g_ceph_context` config at construction time, so tests and dynamic config must account for initialization timing. Engine references must outlive requests and appliers/completers they produce. EC2 auth cannot fully support streaming AWSv4 completers unless a secret key is available.

## Test Signals

Compile tests should validate construction with token extractors, remote applier factories, and S3 version abstractors. Runtime tests should validate cache thread safety, token extraction wiring, and EC2 engine behavior through the AWS engine interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_registry.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_auth_registry.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_registry.h` defines `StrategyRegistry`, the aggregate that owns RGW's main authentication strategies and exposes them to request dispatch. The source was read as a complete 97-line header.

## Important APIs, Types, and Functions

`StrategyRegistry` owns `s3_main_strategy`, `s3_post_strategy`, `swift_strategy`, and `sts_strategy`. The nested `s3_main_strategy_t` combines a general S3 AWS strategy that allows anonymous fallback with a Boto2-compatible strategy. Public accessors return references to each strategy, and `create()` returns a `std::unique_ptr<StrategyRegistry>`. Aliases `rgw_auth_registry_t` and `rgw_auth_registry_ptr_t` preserve legacy naming.

## Control Flow

Construction builds all strategies with Ceph context, implicit tenant context, and SAL driver. `s3_main_strategy_t` adds the normal general S3 strategy as `SUFFICIENT`, then adds Boto2 as `FALLBACK`. Callers choose the correct strategy for S3 main requests, S3 browser uploads, Swift, or STS.

## State and Persistence Behavior

The registry owns long-lived strategy objects and their embedded engines for the current RGW configuration. It has no persistence and no mutable runtime state beyond the strategies it contains.

## Dependencies and Integration Points

It depends on core auth interfaces, S3 auth, Swift auth, and STS REST auth. It is the central construction point for request-layer code that needs the current authentication strategy after initialization or realm/config reconfiguration.

## Risks and Edge Cases

Adding a new auth strategy or engine requires exposing it here or it will not participate in request authentication. The S3 main order is security-sensitive: a `SUFFICIENT` normal strategy short-circuits success, while Boto2 only influences fallback failures. Anonymous access is enabled only on the plain main strategy template parameter.

## Test Signals

Tests should assert registry construction, strategy non-emptiness, expected strategy names/orders, S3 fallback behavior, and that Swift/STS accessors return stable references for the registry lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_registry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.cc` implements S3 signature canonicalization, AWS Signature Version 2 and Version 4 parsing/signing helpers, streaming AWSv4 payload completers, trailer signature validation, canonical method selection, and auth-type logging helpers. The source was read as a complete 1782-line implementation.

## Important APIs, Types, and Functions

Top-level helpers include `rgw_create_s3_canonical_header()` overloads, `get_canon_resource()`, `get_canon_amz_hdrs()`, and `get_v2_qs_map()`. In `rgw::auth::s3`, important functions include `is_time_skew_ok()`, `parse_v4_credentials()`, `gen_v4_scope()`, `get_v4_canonical_qs()`, `gen_v4_canonical_qs()`, `get_v4_canonical_headers()` overloads, `get_v4_canon_req_hash()`, `get_v4_string_to_sign()`, `get_v4_signature()`, `get_v2_signature()`, `get_canonical_method()`, and `get_aws_version_and_auth_type()`. Completer logic lives in `AWSv4ComplMulti::ChunkMeta`, `AWSv4ComplMulti`, and `AWSv4ComplSingle`.

## Control Flow

Signature v2 canonicalization validates Content-MD5 base64 characters, chooses Date/Expires behavior for header vs query auth, parses request time, gathers x-amz metadata/query security token fields, orders signed subresources, and emits the string to sign. Signature v4 parsing handles query-string presign fields or Authorization header key/value fields, validates dates/time skew, splits credential scope, extracts access key id, builds canonical query strings and headers, hashes canonical requests, builds strings to sign, derives signing keys, and computes server signatures.

For streaming AWSv4, `AWSv4ComplMulti` installs itself as an IO filter, parses chunk metadata, verifies each previous chunk signature after the next chunk boundary is known, streams payload bytes while updating SHA256, adjusts decoded content length, consumes final zero-length chunk/trailer bytes, optionally extracts declared trailing headers into request properties, and validates trailer signatures when expected. `AWSv4ComplSingle` filters non-chunked signed bodies and validates the final payload hash in `complete()`.

## State and Persistence Behavior

The file does not persist state externally. It mutates request state by installing auth filters, updating decoded content length, adding trailer-derived properties, and populating auth logging strings. Completers keep in-memory stream position, current chunk metadata, previous chunk signature, signing key, SHA256 contexts, parsing buffers, and trailer expectations for the lifetime of a request body.

## Dependencies and Integration Points

Dependencies include RGW REST/S3 request structures, HTTP environment maps, `rgw_client_io`, Ceph crypto/HMAC/SHA helpers, UTF-8 encoding, URL recoding, query parsing, CORS method validation, sanitized logging, and AWS auth abstractor types declared in `rgw_auth_s3.h`. The output feeds S3/Keystone AWS engines by producing string-to-sign values, signature factories, and completer factories.

## Risks and Edge Cases

Canonicalization is compatibility-sensitive: query parameter ordering, slash encoding, host port handling for Boto2 presigned URLs, signed subresource lists, whitespace trimming, and non-S3 operation parameter filtering can change auth outcomes. Presigned v4 expiration is capped at seven days and maps expiration to special errors. Chunk parsing uses fixed metadata and trailer buffer limits, supports signed and unsigned chunked modes, and must correctly handle boundary variants with optional leading CRLF. Missing signed headers are tolerated by skipping unavailable env vars, which can affect compatibility/security expectations. Secrets and strings-to-sign are logged only through sanitizing paths in some but not all diagnostic branches.

## Test Signals

Tests should cover SigV2 canonical strings for headers/query/subresources, invalid Content-MD5 rejection, SigV4 header and query parsing errors, time skew and presigned expiration, canonical query sorting and plus-to-space handling, canonical header trimming and host-port Boto2 compatibility, non-S3 operation canonical method/query behavior, signing-key derivation, v2/v4 signature matches against AWS examples, single-payload hash completion, signed chunked streaming with trailers, unsigned chunked streaming, final chunk/trailer signature mismatch, trailer buffer limit, and CORS OPTIONS canonical method validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.cc -->
