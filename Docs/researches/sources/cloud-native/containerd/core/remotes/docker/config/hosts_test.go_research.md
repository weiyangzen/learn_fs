<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/hosts_test.go

Purpose: deterministic unit tests for default registry host config, hosts.toml parsing, Docker cert directory fallback, and HTTP fallback selection.

Important APIs/types/functions: `TestDefaultHosts`, `TestParseHostFile`, `TestLoadCertFiles`, `TestHTTPFallback`, comparison/printing helpers, and `testKey`.

Control flow: tests compare returned host configs field-by-field, including scheme/host/path/capabilities/CA/client pairs/skipVerify/headers/dial timeout. Cert tests create `.crt`, `.cert`, and `.key` files and load them through `loadHostDir`. Fallback tests generate many host/default scheme/TLS cases and inspect returned scheme plus transport type.

State and persistence: uses temp directories and test certificate/key files. No network requests.

Dependencies and integration points: validates `hosts.go`, `config_unix.go`/`config_windows.go` path behavior, and `docker.NewHTTPFallback` selection assumptions.

Risks covered: host table ordering, `override_path`, no-referrers capability omission, header list parsing, client cert shape variants, localhost/port HTTP-vs-HTTPS defaults, and default Docker Hub mapping.

Test signals: broad unit coverage for config parsing and defaulting; semantic network behavior is covered by `hosts_resolver_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts_test.go -->
