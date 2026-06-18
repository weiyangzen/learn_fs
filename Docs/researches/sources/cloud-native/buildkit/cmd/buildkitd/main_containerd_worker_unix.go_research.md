# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker_unix.go

Purpose: provides Unix runtime option type selection for containerd worker runtime configuration.

Important API: `getRuntimeOptionsType` returns `runcoptions.Options` for `plugins.RuntimeRuncV2`; otherwise it returns generic `runtimeoptions.Options`. The selected struct is the TOML unmarshal target for configured runtime options.

State and dependencies: no persistence here; it shapes how config data is decoded before being passed to containerd. Depends on containerd runtime option packages and plugin runtime names.

Risks and test signals: choosing the wrong options type would drop or reject runtime-specific options. There are no direct tests for this mapping in the subset.
