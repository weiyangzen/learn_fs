# sources/cloud-native/soci-snapshotter/service/resolver/registry.go

Purpose: this file builds registry host resolution for remote image access. It adapts SOCI snapshotter resolver configuration, retryable HTTP behavior, registry mirrors, and credential providers into containerd `docker.RegistryHost` values used by source label resolution and filesystem pulls.

Important APIs and types: `Credential` resolves username/secret for an image reference and host; `RegistryHosts` returns containerd registry hosts for an image reference; `RegistryManager` owns the retry client, global headers, resolver config, credential providers, and a `sync.Map` cache keyed by `reference.Spec.String()`. `NewRegistryManager` wires retry and header defaults. `AsRegistryHosts` returns the closure consumed by containerd remote resolver code. `multiCredsFuncs` chains credential providers in order and stops at the first non-empty credential. `DefaultScheme` forces HTTP for localhost and HTTPS elsewhere.

Control flow: `AsRegistryHosts` first checks the per-image cache. On a miss, it creates a per-image auth client with `multiCredsFuncs`, expands any configured mirrors for `imgRefSpec.Hostname()`, then appends the canonical upstream host. Mirror URLs are parsed, normalized through `docker.DefaultHost`, and default to `/v2` if no path is provided. Mirror `Insecure` changes scheme to HTTP. Per-mirror request timeouts clone the retryable client and auth client while reusing the global transport.

State and persistence: state is in-memory only. The cache can retain registry host configurations for the life of the process. Because credentials can be image/repository scoped, the auth client is intentionally created per image reference, not globally per host.

Dependencies and integration points: depends on `config.ResolverConfig`, HashiCorp retryablehttp, containerd `remotes/docker`, and local auth helpers in the resolver package. It is used by `service.NewSociSnapshotterService` through `source.RegistryHosts`.

Risks: `int64(retryClient.HTTPClient.Timeout)` compares a nanosecond duration to a configured seconds value, so timeout equality detection is suspicious and may clone more often than intended. Cached `RegistryHost` slices may also freeze credential-provider behavior for an image reference if provider semantics or resolver config are changed at runtime. Mirror URL parsing trusts `url.Host`; malformed mirror strings without a scheme may produce empty hosts.

Test signals: this file has no direct test in the requested set, but resolver behavior is likely covered by neighboring resolver tests. Important test gaps are mirror timeout handling, per-image credential scoping, and invalid mirror URL forms.
