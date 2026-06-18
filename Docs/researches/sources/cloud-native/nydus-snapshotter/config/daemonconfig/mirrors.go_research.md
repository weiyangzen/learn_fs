# sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirrors.go

Purpose: parse containerd-style registry `hosts.toml` mirror configuration with Nydus health metadata.

Flow: resolves host-specific, port-escaped, or `_default` directories; parses ordered `[host]` TOML entries by source line; supports headers, CA cert strings/arrays, skip_verify/client fields in schema, and Nydus `health_check_interval`, `failure_limit`, `ping_url`; deduplicates CA certs across hosts.

State/dependencies: reads files under mirror config root; no writes. Depends on go-toml and net/http header types.

Integration points: called by `selectMirrorHost` before nydusd backend host rewrite.

Risks/tests: `server` top-level is parsed but not used as fallback host. Relative CA path handling is not normalized. Tests cover defaults, host precedence, headers, and CA dedupe.
