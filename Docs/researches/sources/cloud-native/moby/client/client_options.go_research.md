<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_options.go -->
# sources/cloud-native/moby/client/client_options.go

Purpose: defines the functional option system for constructing `Client` instances, including environment configuration, host/transport/TLS setup, API version overrides, tracing, headers, timeout, and response hooks.

Important APIs/types/functions: `clientConfig`, `ResponseHook`, `Opt`, `FromEnv`, `WithDialContext`, `WithHost`, `WithHostFromEnv`, `WithHTTPClient`, `WithTimeout`, `WithUserAgent`, `WithHTTPHeaders`, `WithScheme`, `WithTLSClientConfig`, `WithTLSClientConfigFromEnv`, `WithAPIVersion`, deprecated `WithVersion`, `WithAPIVersionFromEnv`, deprecated `WithVersionFromEnv`, no-op deprecated `WithAPIVersionNegotiation`, `WithTraceProvider`, `WithTraceOptions`, and `WithResponseHook`.

Control flow: `FromEnv` applies TLS, host, then API version env options. `WithHost` parses the host, updates proto/addr/basePath, and reconfigures the underlying `http.Transport` unless using the package test transport. `WithHTTPClient` clones caller clients/transports to avoid mutating external state. TLS options either mutate the existing transport or, for env TLS, replace the client with a TLS-configured one. API version options trim optional `v`, validate syntax, and store manual/env override slots for `New` to resolve.

State and persistence behavior: state is entirely in the in-memory `clientConfig`; TLS options read certificate files named by arguments or `DOCKER_CERT_PATH` but do not write. Environment options read `DOCKER_HOST`, `DOCKER_API_VERSION`, `DOCKER_CERT_PATH`, and `DOCKER_TLS_VERIFY`.

Dependencies and integration points: uses docker go-connections sockets/TLS helpers, containerd errdefs for duplicate header validation, OpenTelemetry tracing options, and `parseAPIVersion`. Endpoint requests later consume configured headers, user agent, scheme, client, and hooks.

Risks and test signals: risks include option order surprises, env/manual API version precedence, duplicate header canonicalization, replacing transports during TLS env setup, and nil response hooks. `client_options_test.go` covers host/env behavior, timeouts, API version parsing and priority, user agent/header rules, cloned HTTP clients, and response hook validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_options.go -->
