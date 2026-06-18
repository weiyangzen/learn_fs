# sources/cloud-native/moby/client/plugin_upgrade.go

## Purpose
`plugin_upgrade.go` implements plugin upgrade with the same permission/authentication contract used by plugin install.

## Important APIs, Types, And Functions
Types: `PluginUpgradeOptions`, `PluginUpgradeResult`. Functions: `PluginUpgrade`, `tryPluginUpgrade`, `getRegistryAuth`, `setRegistryAuth`, `getPrivilegeFunc`, `getAcceptAllPermissions`, `getAcceptPermissionsFunc`, `getRemoteRef`. Important fields: `PluginUpgradeOptions` has `Disabled`, `AcceptAllPermissions`, `RegistryAuth`, `RemoteRef`, `PrivilegeFunc`, `AcceptPermissionsFunc`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins/`, `/upgrade`; uses client helper(s) `post`. Unauthorized registry responses can trigger a caller-provided privilege callback and one retry with refreshed `X-Registry-Auth`. Image or plugin references are normalized before request construction, preventing malformed names from reaching the daemon.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `fmt`, `io`, `net/http`, `net/url`, `github.com/distribution/reference`, `github.com/moby/moby/api/types/plugin`, `github.com/moby/moby/api/types/registry`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks; auth retry paths must close failed responses and preserve the refreshed header.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
