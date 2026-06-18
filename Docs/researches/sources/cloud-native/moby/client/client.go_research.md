<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client.go -->
# sources/cloud-native/moby/client/client.go

Purpose: defines the Docker/Moby Engine API `Client`, its default construction path, host parsing, version negotiation, redirect policy, raw dialers, and package-level API version constants. It is the central integration point for all endpoint wrapper files in this package.

Important APIs/types/functions: `Client`, `New`, deprecated `NewClientWithOpts`, `CheckRedirect`, `Close`, `ClientVersion`, `DaemonHost`, `ParseHostURL`, `Dialer`, `MaxAPIVersion`, `MinAPIVersion`, `DummyHost`, and `ErrRedirect`. `Client` embeds `clientConfig`, stores an atomic `negotiated` flag, a negotiation mutex, and `baseTransport` for direct transport operations such as closing idle connections and extracting dialers.

Control flow: `New` parses `DefaultDockerHost`, creates a default `http.Client`, applies functional options in caller order, resolves API version override precedence, stores the base transport when possible, infers `http` vs `https` from TLS configuration, wraps transport with OpenTelemetry, then optionally wraps it with response hooks. `getAPIPath` lazily triggers `Ping`-based negotiation, prefixes paths with `/v<version>` when a version is configured, and appends encoded query values. `negotiateAPIVersion` parses daemon ping version, rejects versions below `MinAPIVersion`, and downgrades from `MaxAPIVersion` when needed.

State and persistence behavior: client state is in-memory only: configured host/proto/address/version, negotiation completion, transport wrappers, idle connections, custom headers, hooks, and trace options. It persists no files. `Close` only closes idle connections on the saved base transport.

Dependencies and integration points: depends on `github.com/docker/go-connections/sockets` for `unix`, `npipe`, and TCP transport setup; containerd errdefs for invalid version errors; internal `versions` parsing/comparison; internal module version lookup for the default user agent; OpenTelemetry HTTP transport wrapping. Endpoint files depend on `getAPIPath`, request helpers, and `dialer`/`postHijacked`.

Risks and test signals: important risks are API negotiation races, option precedence, local-socket host handling via `DummyHost`, redirects changing non-GET semantics, and transport wrapper ordering. `client_test.go` covers construction, host parsing, API path generation, negotiation paths, fixed versions, connection failure behavior, and redirect policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client.go -->
