<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authprovider.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/authprovider.go

Purpose: implements the client-side session Auth service that shares Docker registry credentials, fetches bearer tokens, handles registry TLS overrides, and proves token authority.

Important APIs, types, and functions: constants define default token expiration and Docker Hub host/key names. `AuthConfigProvider`, `ExpireCachedAuthCheck`, and `DockerAuthProviderConfig` configure providers. `NewDockerAuthProvider` creates a session attachable with default 4m50s cache expiration. `authProvider` implements generated `AuthServer`, logger support, TLS config assembly, credential conversion, token fetching, credential sharing, token authority key derivation, and scope label trimming.

Control flow and state: provider state includes an auth config provider, token seed store, optional logger, logger cache, TLS configs, and a mutex protecting credential-helper access and logging. `FetchToken` loads auth config, returns static registry token when present, otherwise calls OAuth token endpoint when credentials exist and falls back to GET token for known POST failures, or fetches anonymous token. `Credentials` returns username/password or identity token and logs first share per host. Token authority derives an Ed25519 key from HMAC(salt, seed) only when a secret exists, unless disabled by `BUILDKIT_NO_CLIENT_TOKEN`.

Dependencies and integration: uses containerd Docker auth helpers, Docker CLI config types, tracing HTTP transport, BuildKit progress logging, generated auth server registration, and NaCl signing.

Risks and test signals: security-sensitive paths include client token seed persistence, salt handling, and TLS override loading. The `tracing.DefaultClient` assignment can share mutable HTTP client state. Existing tests cover token cache expiration. Additional tests should cover OAuth fallback statuses, TLS config loading, token authority disablement, identity-token credential conversion, and concurrent credential-helper access.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authprovider.go -->
