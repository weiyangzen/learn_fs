# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker_windows.go

Purpose: provides Windows runtime option type selection for containerd worker runtime configuration.

Important API: `getRuntimeOptionsType` returns `runhcsoptions.Options` for `plugins.RuntimeRunhcsV1`; otherwise it returns generic `runtimeoptions.Options`. This allows TOML runtime options to decode into the correct Windows shim struct.

State and dependencies: no persistence here; decoded options are later included in containerd worker runtime info. Depends on hcsshim runhcs options and containerd plugin constants.

Risks and test signals: a mismatched runtime type can make Windows containerd worker startup fail or ignore options. There are no direct tests for this mapping.
