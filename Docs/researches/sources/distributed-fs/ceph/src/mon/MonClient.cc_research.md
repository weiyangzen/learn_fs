# sources/distributed-fs/ceph/src/mon/MonClient.cc

## Purpose

`MonClient.cc` implements the client-side monitor connection manager. It builds and refreshes monmaps, hunts for a monitor session, authenticates, renews subscriptions and auth tickets, sends monitor commands and tell commands, handles config pushes, sends log messages, serves authorizer requests for peer services, and exposes an admin socket key-rotation hook.

## Important APIs, Types, and Functions

Major functions include `build_initial_monmap()`, `get_monmap()`, `get_monmap_and_config()`, `ping_monitor()`, `ms_dispatch()`, `handle_monmap()`, `handle_config()`, `init()`, `shutdown()`, `authenticate()`, `_reopen_session()`, `_add_conns()`, `_finish_hunting()`, `tick()`, `_renew_subs()`, `_check_auth_tickets()`, `_check_auth_rotating()`, `wait_auth_rotating()`, `_send_command()`, `_check_tell_commands()`, `_resend_mon_commands()`, command reply handlers, version reply handling, AuthClient/AuthServer callbacks, and all `MonConnection` auth helpers. The custom `monc_category()` maps local async errors to standard conditions and negative errno values.

## Control Flow and State

The session state machine is protected by `monc_lock`. When no session is open, `_reopen_session()` clears active/pending state, starts hunting, connects to configured target rank or a weighted shuffled batch of monitors, starts auth handshakes, clears old queued messages, cancels version requests with `session_reset`, and renews subscriptions. On auth success, `_finish_hunting()` installs `active_con`, sends queued messages, resends commands, flushes logs, moves auth state, and records global id. `tick()` drives reconnect hunting, subscription renewals for non-stateful-sub monitors, keepalives and keepalive timeout reconnects, log sending, auth ticket checks, rotating-key refreshes, and tell command retries.

Command flow supports normal `MMonCommand` over the active session and directed tell commands. For Octopus and later, tell commands open anonymous direct monitor connections with their own `MonConnection`; legacy monitors force the main session to the target rank/name. Commands are completed asynchronously on the Boost.Asio service executor, and timeout timers cancel outstanding commands.

State includes monmap, config manager values, active and pending monitor connections, tried monitor ranks, auth handlers, rotating secrets, subscriptions, queued messages, outstanding commands, version requests, timers, log state, bootstrap config state, and config callbacks.

## Dependencies and Integration Points

Dependencies include Messenger, Dispatcher, AuthClient/AuthServer, AuthRegistry, KeyRing, RotatingKeyRing, monitor messages, LogClient, AdminSocket, SafeTimer, Boost.Asio, weighted shuffle, mon feature bits, and error categories. It is the shared monitor access layer for clients, daemons, and bootstrap config retrieval.

## Risks and Test Signals

Risks include lock-sensitive callback paths, stale stray monitor messages, global-id changes across reconnects, clearing queued messages on reopen, version request cancellation semantics, tell-command retry limits, auth method fallback, rotating-key renewal frequency and clock skew, passthrough monmap ownership, and config callback execution outside `monc_lock`. Tests should cover hunt success/failure, weighted rank selection, monmap epoch update clearing `tried`, msgr2 reconnect decisions, auth bad-method fallback, shutdown cancellation, command timeout and directed command errors, keepalive reconnects, subscription renewals, config bootstrap, version request replies, and `monc_errc` conversions.
