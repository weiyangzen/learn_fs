# sources/cloud-native/moby/client/plugin_install.go

## Purpose
`plugin_install.go` implements multi-step plugin installation: privilege lookup, permission acceptance, pull progress streaming, optional argument setting, and optional enablement.

## Important APIs, Types, And Functions
Types: `PluginInstallOptions`, `PluginInstallResult`, `pluginOptions`. Functions: `PluginInstall`, `tryPluginPrivileges`, `tryPluginPull`, `checkPluginPermissions`, `getRegistryAuth`, `setRegistryAuth`, `getPrivilegeFunc`, `getAcceptAllPermissions`, `getAcceptPermissionsFunc`, `getRemoteRef`. Important fields: `PluginInstallOptions` has `Disabled`, `AcceptAllPermissions`, `RegistryAuth`, `RemoteRef`, `PrivilegeFunc`, `AcceptPermissionsFunc`; `PluginInstallResult` has `io.ReadCloser`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins/`, `/plugins/privileges`, `/plugins/pull`; uses client helper(s) `delete`, `get`, `post`. Unauthorized registry responses can trigger a caller-provided privilege callback and one retry with refreshed `X-Registry-Auth`. Image or plugin references are normalized before request construction, preventing malformed names from reaching the daemon.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `errors`, `fmt`, `io`, `net/http`, `net/url`, `github.com/containerd/errdefs`, `github.com/distribution/reference`, `github.com/moby/moby/api/types/plugin`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks; auth retry paths must close failed responses and preserve the refreshed header; install cleanup depends on the goroutine observing `retErr`; streaming failures can affect rollback behavior.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
