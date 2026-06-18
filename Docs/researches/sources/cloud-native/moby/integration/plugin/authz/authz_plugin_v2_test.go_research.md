# sources/cloud-native/moby/integration/plugin/authz/authz_plugin_v2_test.go

## Purpose
Tests managed v2 authorization plugin behavior: install, enable as daemon authorization plugin, allow non-volume requests, reject volume APIs, disable plugin recovery, and daemon startup failure for bad/nonexistent plugins.

## Important APIs, Types, And Functions
Defines plugin image names and `setupTestV2`, which requires non-Windows, Docker Hub connectivity, and starts a daemon. `pluginInstallGrantAllPermissions` calls `PluginInstall` with `AcceptAllPermissions` and drains the response body to EOF.

## Control Flow
Tests install remote plugins, restart the daemon with `--authorization-plugin=<plugin>`, and execute Docker APIs. Allow test runs a container and inspects it. Reject tests call volume create/list/remove/inspect/prune and assert plugin failure messages. Bad manifest and nonexistent plugin tests expect daemon restart errors, then verify daemon can start without the plugin.

## State And Persistence Behavior
Plugin installation persists in daemon plugin state across daemon restart. Disabling the plugin is tested as a live state transition that restores volume API access.

## Dependencies And Integration Points
Depends on Docker Hub connectivity, amd64 plugin images, plugin install/enable/disable APIs, daemon restart, volume APIs, and the authorization plugin manifest contract.

## Risks
Remote image availability and registry connectivity are major risks. Tests skip non-amd64 and Windows, but still depend on plugin image names remaining valid. Restart failure assertions are coarse and could miss detailed reason changes.

## Test Signals
Signals are successful non-volume container inspect, volume API errors containing the plugin name, successful API call after disable, and expected restart errors for invalid plugin configuration.
