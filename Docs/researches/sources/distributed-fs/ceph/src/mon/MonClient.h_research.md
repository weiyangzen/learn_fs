# sources/distributed-fs/ceph/src/mon/MonClient.h

## Purpose

`MonClient.h` declares Ceph's monitor client abstraction and its per-connection auth helper. It is the public surface for acquiring monmaps/config, authenticating, sending monitor commands, managing monitor subscriptions, serving authorizers, and exposing monitor connectivity state to daemons and clients.

## Important APIs, Types, and Functions

`MonConnection` owns one monitor `ConnectionRef`, auth state, global id, and optional queued tell command. It exposes v1/v2 auth request and response helpers plus session state queries. `MonClientPinger` is a standalone dispatcher/auth client for isolated monitor ping operations. `monc_errc` defines async errors for shutdown, session reset, missing rank/name, timeout, and monitor unavailability.

`MonClient` derives from `Dispatcher`, `AuthClient`, `AuthServer`, and `AdminSocketHook`. Public APIs include `init()`, `shutdown()`, `build_initial_monmap()`, `get_monmap()`, `get_monmap_and_config()`, `ping_monitor()`, `send_mon_message()`, `reopen_session()`, auth/key methods, subscription methods, monmap accessors, `build_authorizer()`, async `start_mon_command()` overloads, Context-based command wrappers, async `get_version()`, `with_monmap()`, and config callback registration.

## Control Flow and State

The header separates active monitor session state (`active_con`) from hunting state (`pending_cons`, `tried`). It stores auth state, timer state, subscription state, waiting messages, outstanding command map, version request map, bootstrap config state, and config callback hooks. Async command and version APIs use Boost.Asio completion handlers and consign work guards so completions remain valid.

## Dependencies and Integration Points

Dependencies include Boost.Asio, Messenger/Dispatcher, MonMap, MonSub, AdminSocket, Timer, config, auth client/server classes, keyrings, command messages, and Ceph contexts. Consumers use this class across client mount, daemon startup, monitor command execution, config delivery, and service-to-service authentication.

## Risks and Test Signals

The API mixes synchronous waits, lock-protected state, and asynchronous completions. Tests should validate callback completion on shutdown, Context wrapper conversion, directed command target parsing, subscription locking, `with_monmap()` lock usage, auth-server authorizer handling, and public accessors while hunting or stopped.
