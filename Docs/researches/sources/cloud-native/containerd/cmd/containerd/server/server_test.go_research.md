# sources/cloud-native/containerd/cmd/containerd/server/server_test.go

Purpose: validates server directory setup errors and plugin config migration integration through `server.New()`.

Important APIs/functions tested: `CreateTopLevelDirectories()`, `srvconfig.LoadConfigWithPlugins()`, plugin `ConfigMigration`, and `New()`.

Control flow: directory tests assert root/state empty or equal paths fail with exact errors. `TestMigration` registers temporary plugins, writes an older-version config, runs config loading with plugin migration callbacks, and initializes a server to ensure migrated config reaches the correct plugin.

State and persistence: uses temporary config files and resets global plugin registry around migration test.

Dependencies/integration: uses plugin registry graph ordering, TOML marshal, version config number, and `testify/assert`.

Risks covered: prevents invalid root/state combinations and verifies plugin migration data can move between plugin IDs before initialization.

Test gaps: does not start server listeners, stop plugins, test readiness, or cover proxy plugin registration.
