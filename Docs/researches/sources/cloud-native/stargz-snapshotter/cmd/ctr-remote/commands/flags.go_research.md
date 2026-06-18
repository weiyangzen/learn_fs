# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/flags.go

Purpose: Defines sampler/container runtime flags and converts CLI input into OCI spec options used by `optimize` analysis containers.

Important APIs: `samplerFlags`, `parseGPUs`, `getSpecOpts`, `withEntrypointArgs`, `withCNI`, `withResolveConfig`, `parseMountFlag`, `parseResolveFlag`, and `withStaticCDIRegistry`.

Control flow: `getSpecOpts` builds cleanup-aware OCI spec options: default spec/devices/rootfs/image/env/mounts, DNS/hosts bind mounts, optional env file/user/cwd/TTY, optional CNI network namespace setup, host networking, and GPU CDI device injection. `withEntrypointArgs` loads image config and overrides entrypoint/cmd from JSON flags. `withResolveConfig` creates temporary resolv.conf and hosts files. `withCNI` creates a netns, configures CNI, and returns cleanup that removes network and namespace.

State and persistence: Uses temporary directories for DNS/hosts files and netns mounts under `/var/run/netns`; cleanup callbacks remove them. CDI registry state is refreshed globally with auto-refresh disabled.

Dependencies and integration: Used by `optimize.go` via `analyzer.WithSpecOpts`. Integrates containerd OCI helpers, go-cni, netns, runtime-spec, CDI, and image config blobs.

Risks: Cleanup errors are aggregated but an error-wrapping bug can lose the cleanup error detail. Mount parsing is simple key/value CSV and rejects unknown keys. GPU parser ignores non-numeric non-`all` entries.

Test signals: No direct tests in this subset; flag parsing and cleanup deserve focused tests.
