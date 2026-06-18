# sources/cloud-native/moby/integration-cli/docker_cli_plugins_logdriver_test.go

Purpose: validates v2 plugin log drivers for container logs and daemon info reporting.

Important APIs and functions: `DockerCLIPluginLogDriverSuite`, `cli.DockerCmd`, Engine `client.Info`, `client.New(client.FromEnv)`, and `testutil.GetContext`.

Control flow: `TestPluginLogDriver` installs `cpuguy83/docker-logdriver-test:latest`, runs a container with `--log-driver`, checks logs after first run, starts it attached again, checks accumulated logs, then removes container and plugin. `TestPluginLogDriverInfoList` installs the plugin, reads daemon info through the API, joins `info.Plugins.Log`, and asserts built-in `json-file` appears while the v2 plugin name does not.

State and persistence: installs and removes a daemon plugin, creates log records for a named container, and reads daemon plugin metadata.

Dependencies and integration points: Linux amd64 daemon, network/plugin distribution access, Docker plugin subsystem, log driver integration, and daemon info API.

Risks: plugin availability and architecture are external; log output accumulation can fail if the driver changes retention semantics; info-list behavior is intentionally subtle because v2 plugins should not appear in the legacy log plugin list.

Test signals: containers using the plugin log driver produce retrievable logs, repeated starts append as expected, and daemon info separates built-in log drivers from v2 plugin drivers.
