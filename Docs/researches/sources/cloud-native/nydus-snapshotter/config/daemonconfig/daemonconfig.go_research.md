# sources/cloud-native/nydus-snapshotter/config/daemonconfig/daemonconfig.go

Purpose: common daemon config interface, backend config model, config dumping, snapshot-specific supplementation, mirror selection, and secret filtering.

Flow: `NewDaemonConfig` loads fscache or fuse config by fs driver. `SupplementDaemonConfig` parses image reference, rewrites docker.io host, optionally converts VPC registry, selects mirror/CA certs, fills repo/host/snapshot params/auth, or only supplements workdir for non-registry backends. `DumpConfigFile` writes atomically and optionally filters secret fields.

State/dependencies: writes JSON config files via temp+rename; calls mirror health URLs; reads global config.

Integration points: used before launching/communicating with nydusd.

Risks/tests: mirror ping logging uses `err` instead of `pingErr` in warning paths. Secret filter is reflection-based and may mishandle unexported/unexpected fields. Tests cover JSON parsing, amplify_io, and secret filtering.
