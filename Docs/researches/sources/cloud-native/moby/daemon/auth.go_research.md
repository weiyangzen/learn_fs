## sources/cloud-native/moby/daemon/auth.go

**Purpose:** Provides the daemon registry authentication API shim.

**Important APIs:** `AuthenticateToRegistry(ctx, authConfig)` calls `daemon.registryService.Auth` with the supplied `registry.AuthConfig` and Docker user agent from `dockerversion.DockerUserAgent(ctx)`.

**Control flow:** There is no branching; validation and registry interaction are delegated to the registry service.

**State and persistence:** No local state is stored. Any credential verification side effects belong to the registry service or remote registry.

**Dependencies and integration:** Integrates daemon API auth endpoint handling with `daemon.registryService` and API registry types.

**Risks:** Behavior is entirely dependent on the registry service contract. Context user-agent extraction matters for remote registry requests and diagnostics.

**Test signals:** No direct test in this subset; registry package tests elsewhere should cover auth behavior. This wrapper mainly needs compile/interface coverage.
