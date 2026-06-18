# sources/cloud-native/moby/integration/plugin/authz/main_test.go

## Purpose
Package-level harness for non-Windows authz plugin integration tests. It initializes tracing/environment, creates per-test daemon instances, and hosts a fake authorization plugin server that implements the Docker plugin activation and authorization request/response endpoints.

## Important APIs, Types, And Functions
`TestMain` configures tracing, initializes `environment.Execution`, ensures frozen Linux images, calls `setupSuite`, runs tests, and tears down the HTTP server. `setupTest` skips remote daemons/Windows, protects the environment, creates an experimental daemon, and schedules daemon/environment cleanup. `setupSuite` creates an `httptest.Server` with handlers for `/Plugin.Activate`, `/AuthZPlugin.AuthZReq`, and `/AuthZPlugin.AuthZRes`. `assertAuthHeaders` and `assertBody` enforce sanitization rules.

## Control Flow
The fake plugin server marshals a manifest implementing `authorization.AuthZApiImplements`. Request and response handlers decode `authorization.Request`, reject leaked auth headers, reject bodies for auth or non-text/non-JSON requests, count `/version` hooks, record URIs, choose configured responses from global `ctrl`, and write JSON `authorization.Response`.

## State And Persistence Behavior
Global state includes `testEnv`, `d`, `server`, `baseContext`, and the `ctrl` object created by individual tests. The server persists for the package run; daemon instances are per test.

## Dependencies And Integration Points
Integrates plugin contract types from `pkg/plugins` and `pkg/authorization`, `otelhttp`, Moby daemon test utilities, and the authz tests' global controller.

## Risks
Panics in HTTP handlers fail tests abruptly. Operator precedence in `assertBody` is significant: JSON content type returns early because of the `|| v == "application/json"` clause. Shared globals make parallel tests unsafe unless isolated.

## Test Signals
Harness signals are indirect: tests fail if plugin activation manifest is wrong, if auth headers/bodies leak to the plugin, or if daemon setup/cleanup fails.
