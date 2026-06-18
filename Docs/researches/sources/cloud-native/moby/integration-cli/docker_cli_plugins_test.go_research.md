# sources/cloud-native/moby/integration-cli/docker_cli_plugins_test.go

Purpose: broad Docker plugin lifecycle tests for install, disable, enable, remove, active-use protection, setting configurable fields, create/inspect/list/upgrade, ID prefix addressing, default formatting, and plugin metrics.

Important APIs and functions: `DockerCLIPluginsSuite`, `DockerPluginSuite` methods such as `getPluginRepoWithTag`, plugin helpers from `internal/testutil/plugin`, `plugintypes`, Engine API client via `testEnv.APIClient`, `cli.DockerCmd`, `dockerCmdWithError`, temp filesystem creation for `plugin create`, and HTTP metrics reads.

Control flow: tests install plugins with and without `--disable`, verify active volume/network plugins cannot be disabled/removed until resources are removed, mutate settable env/mount/device fields, reject invalid set operations, install with args, reject installing a container image as a plugin, check duplicate enable/disable errors, create plugins from a local config/rootfs, inspect by full ID, short ID, tag, and untagged name, verify Windows unsupported errors, operate by ID prefix, honor `pluginsFormat`, upgrade only after disable, and fetch metrics from a plugin endpoint.

State and persistence: installs plugins into daemon plugin storage, creates volumes/networks, writes local plugin config/rootfs directories, touches plugin rootfs files during upgrade, and reads daemon root plugin paths. Plugin enable/disable state and settings are persisted and inspected.

Dependencies and integration points: Linux amd64 plugin runtime, private/public plugin registries, network access, Docker volume/network subsystems, daemon root directory, HTTP metrics endpoint, and platform gates.

Risks: external plugin images can disappear or change; upgrade test inspects daemon internals; metrics port conflicts are possible; test state is heavy and requires careful cleanup.

Test signals: plugin lifecycle commands must enforce active-use constraints, preserve and expose settings, resolve IDs consistently, format lists according to config, reject unsupported artifacts/platforms, upgrade rootfs only when disabled, and expose plugin-provided metrics.
