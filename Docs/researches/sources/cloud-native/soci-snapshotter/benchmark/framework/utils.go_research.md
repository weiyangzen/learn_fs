# sources/cloud-native/soci-snapshotter/benchmark/framework/utils.go

Purpose: registry pull helper utilities for benchmark containerd processes.

Important APIs/types/functions: `ContainerdProcess.PullImageFromRegistry` and `GetResolver`.

Control flow: `PullImageFromRegistry` adds platform remote opts plus a Docker resolver and calls containerd client pull. `GetResolver` parses the image reference, loads default Docker CLI config, extracts credentials for the hostname if present, configures Docker resolver hosts with those credentials, and uses an in-memory push tracker.

State and persistence: reads Docker credential config from the user environment; no writes.

Dependencies/integration: used by benchmark workloads pulling private/public images; depends on containerd remotes/docker config and Docker CLI config loading.

Risks: parse errors panic instead of returning errors. Credential callback returns the same username/password for any host passed to it, though values are selected from the parsed ref hostname. Auth helpers depend on local Docker config availability in CI.

Test signals: pull tests with public images, private registry credentials, invalid image refs, and missing Docker config.
