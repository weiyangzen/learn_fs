# sources/cloud-native/moby/integration/plugin/authz/authz_plugin_test.go

## Purpose
Integration tests for legacy authorization plugin API behavior on non-Windows platforms. The file verifies allow/deny/error paths for request and response authorization hooks, TLS user propagation, event stream behavior, duplicate plugin registration, image load/save/import streaming, container archive copy, and response headers.

## Important APIs, Types, And Functions
Defines `authorizationController`, constants for plugin name/messages/endpoints, `setupTestV1`, `isAllowed`, `socketHTTPClient`, `newTLSAPIClient`, `systemTime`, `systemEventsSince`, image helper functions, and `assertURIRecorded`. It uses `authorization.Response`, Docker client APIs, raw HTTP over daemon socket, TLS client config, `go-archive`, and event stream APIs.

## Control Flow
`setupTestV1` writes `/etc/docker/plugins/authzplugin.spec` pointing at the suite test server and resets global `ctrl`. Tests configure `ctrl.reqRes` and `ctrl.resRes`, start the daemon with `--authorization-plugin`, execute API calls, and assert authorization callbacks and client errors. Allow tests create containers and call `/version`; deny/error tests assert exact daemon error strings and request/response hook counts. Stream and archive tests ensure long-lived or body-heavy APIs pass through authorization without truncation or duplicate registration issues.

## State And Persistence Behavior
State is held in the global `ctrl` request/response controller and plugin spec files under `/etc/docker/plugins`. Temporary image/archive files and containers are created during streaming tests. Cleanup removes plugin specs and stops daemon state through shared setup.

## Dependencies And Integration Points
Depends on the httptest authorization server from `main_test.go`, Docker authorization plugin contract (`/Plugin.Activate`, `/AuthZPlugin.AuthZReq`, `/AuthZPlugin.AuthZRes`), daemon socket HTTP transport, TLS cert fixtures, event APIs, image APIs, archive copy APIs, and Linux-only plugin support.

## Risks
Global mutable `ctrl` requires tests to avoid unsafe parallelism. Exact error message assertions are brittle. Tests that write `/etc/docker/plugins` assume local daemon privileges and can interfere if cleanup fails.

## Test Signals
Signals include request/response callback counts, recorded URI substrings, exact error strings, HTTP 403 status, TLS authenticated user `client`, event stream create/start events, successful image/archive round trips, and JSON content-type preservation.
