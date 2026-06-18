# sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirrors_test.go

Purpose: tests mirror config loading, default fallback, host precedence, headers, and CA cert collection.

Flow: constructs temp certs.d directories and hosts.toml files. Verifies nil when root missing/empty, `_default` fallback, registry-specific override, header extraction, single/array CA parsing, CA dedupe, and nil CA when absent.

State/dependencies: temp filesystem only; uses testify assert/require.

Integration points: confirms compatibility with containerd registry config layout used by snapshotter mirror rewrites.

Risks/signals: does not test malformed header/CA types or port-escaped host directory lookup.
