<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/registry_errors.go -->
# sources/cloud-native/moby/daemon/containerd/registry_errors.go

Purpose: translates containerd/docker registry errors into Docker/Moby error classes with user-facing messages.

Important APIs and flow: `translateRegistryError` returns nil for nil, extracts `docker.Errors`, `remoteerrors.ErrUnexpectedStatus`, or a single `docker.Error`, parses OCI registry error JSON bodies, handles legacy token-server `details` bodies for 401/403, maps known docker error codes to containerd errdefs (`NotImplemented`, `Unauthenticated`, `PermissionDenied`, `Unavailable`, `ResourceExhausted`, `Unknown`), joins multiple errors, and wraps the result as `error from registry`.

State and persistence: none.

Dependencies and integration: used by pull and push error paths. Depends on containerd remotes/docker error types, remote unexpected status bodies, JSON parsing, HTTP status codes, logging, and containerd errdefs.

Risks: failed JSON parsing of an unexpected status body returns an unknown wrapped error, possibly losing registry details. Multiple errors are joined after mapping, which can affect caller matching. Legacy `details` handling only applies when OCI errors array is empty.

Test signals: no direct tests in this subset; high-value tests would cover OCI error arrays, legacy token-server errors, rate limiting, and non-registry pass-through.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/registry_errors.go -->
