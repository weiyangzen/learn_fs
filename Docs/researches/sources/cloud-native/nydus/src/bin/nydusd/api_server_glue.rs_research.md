# sources/cloud-native/nydus/src/bin/nydusd/api_server_glue.rs

## Purpose
`api_server_glue.rs` bridges the generic `nydus_api` HTTP router to the live `nydusd` daemon controller. It maps decoded `ApiRequest` values into daemon, filesystem, blob-cache, metrics, mount, and configuration operations, then sends `ApiResponse` values back to the HTTP router.

## Important APIs, Types, And Functions
`ApiServer` owns the response sender and implements `process_request`, `respond`, daemon operations, metrics exports, mount/remount/umount, fuse-fd save/takeover/start/exit, blob cache entry create/remove/gc, and dynamic config get/update. `ApiServerHandler` owns the request receiver and loops until router shutdown. `ApiServerController` owns router and handler thread handles, the socket path, and a `mio::Waker`; `start` starts the HTTP router and handler thread, while `stop` wakes and joins them and removes the socket file.

## Control Flow
`ApiServerController::start` no-ops when no API socket is configured. Otherwise it creates two channels, builds an `ApiServer`, starts `start_http_thread`, allocates a daemon waker, then spawns the handler thread. The router decodes HTTP into `ApiRequest` and sends it to the handler. `process_request` matches every supported request and calls the corresponding helper. Helpers fetch the daemon or default filesystem service from `DAEMON_CONTROLLER`, perform the operation, map service errors into `ApiError`, and send the response back to the router channel.

## State And Persistence
The controller stores thread handles and a waker. Server operations can persist or mutate daemon state: log level, shutdown, takeover, mount table, blob cache manager entries, upgrade-manager blob entry state, dynamic config values, and blob deletion. `do_exit` triggers daemon exit and sends SIGTERM to the current process. `stop` removes the API socket path.

## Dependencies And Integration Points
This file integrates `nydus_api` routing and payload types, `nydus_service::DaemonController`, `NydusDaemon`, `FsService`, metrics exporters from `nydus_utils::metrics`, Unix signals from `nix`, and the global `DAEMON_CONTROLLER` in `nydusd/main.rs`. It is the server counterpart to `nydusctl/client.rs` and `commands.rs`.

## Risks
`GetBlobObject` is still `todo!()` and would panic if routed. `process_request` unwraps handler errors only to log them, but individual helpers contain unwraps for SIGTERM send and thread joins are only logged. API behavior depends heavily on `DAEMON_CONTROLLER` having a daemon/default filesystem/blob-cache manager set for the selected mode. Config updates accept only keys recognized by `nydus_utils::config::Keys`. Blob cache entry changes update upgrade state only when an upgrade manager exists.

## Test Signals
No unit tests are present. Important integration signals include starting with and without `--apisock`, daemon info v1/v2, log-level updates, start/exit/takeover flows, dynamic mount/remount/umount, metrics routes, config get/update, blob cache create/delete/gc, socket cleanup on stop, and unsupported-mode error responses.
