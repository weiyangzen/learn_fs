# sources/cloud-native/cri-o/internal/criocli/criocli.go

Purpose: centralizes CRI-O CLI default commands, config metadata access, config-file loading, CLI flag merging, flag definitions, string-slice normalization, and timestamp formatting.

Important APIs/types/functions: `DefaultCommands`, `GetConfigFromContext`, `GetAndMergeConfigFromContext`, `mergeConfig`, `mergeConfigFiles`, `mergeRootConfig`, `mergeImageConfig`, `mergeRuntimeConfig`, `mergeRuntimesConfig`, `mergeNetworkConfig`, `mergeAPIConfig`, `mergeMetricsConfig`, `mergeTracingConfig`, `mergeNRIConfig`, `GetFlagsAndMetadata`, `getCrioFlags`, `StringSliceTrySplit`, and `Timestamp`.

Control flow: `GetFlagsAndMetadata` creates default config and flag list, storing the config under app metadata. `GetAndMergeConfigFromContext` loads the config from metadata, then merges config file, config directory, and explicit CLI flags. Merge helpers update only fields whose flags are set, preserving config-file values otherwise. Runtime merge handles conmon, runtimes, hooks, security, capabilities, devices, cgroups, namespace, logging, CRIU, read-only, SELinux, hostport, and timezone settings. `mergeRuntimesConfig` parses colon-delimited runtime handler specs with optional privileged-without-host-devices, config path, and minimum memory.

State and persistence behavior: mutates the in-memory `*libconfig.Config` stored in CLI metadata. It reads config files/drop-ins through `UpdateFromFile` and `UpdateFromPath`. It does not persist merged config except when other commands write output.

Dependencies/integration points: urfave/cli, logrus, Docker units, CRI-O logging, config, and metrics collectors. Every CRI-O command using shared flags depends on this file.

Risks: the large flag list must stay synchronized with `pkg/config` fields, defaults, env vars, and deprecations. `mergeRuntimesConfig` uses colon splitting, so values containing colons are not representable. `StringSliceTrySplit` supports comma fallback only for a single parsed value. Missing config files are skipped only when defaulted; explicit missing config is an error.

Test signals: `criocli_test.go` covers comma splitting copy semantics and two flag merge cases (`hostnetwork-disable-selinux`, `disable-hostport-mapping`), but most flags and runtime parsing are untested here.
