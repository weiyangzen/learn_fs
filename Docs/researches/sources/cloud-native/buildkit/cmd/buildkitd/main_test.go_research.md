# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_test.go

Purpose: unit-tests the `--proxy-network` main daemon flag override behavior.

Important functions and flow: `TestApplyMainFlagsProxyNetwork` starts from empty config and confirms `--proxy-network` sets `cfg.ProxyNetwork` true. `TestApplyMainFlagsProxyNetworkOverridesConfig` starts from true config and confirms `--proxy-network=false` overrides it to false. `runApplyMainFlags` builds a minimal urfave CLI command with only that flag and invokes `applyMainFlags`.

State and dependencies: no persistence; tests mutate in-memory config structs. Dependencies are config package, urfave/cli, context, and testify.

Risks and test signals: this protects a subtle cli v3 bool flag override case where false values must override config. It does not test the rest of `applyMainFlags`, listener creation, TLS, rootless, or worker flags.
